import os
import shutil
import requests
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Global cached embedding model to avoid reloading model weights on every request
_embeddings_instance = None

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
    return _embeddings_instance

def check_ollama_status(ollama_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """Check if Ollama service is active and list available models."""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [m.get("name") for m in models_data]
            return {
                "available": True,
                "models": model_names,
                "message": "Ollama server is active."
            }
    except Exception:
        pass
    return {
        "available": False,
        "models": [],
        "message": "Ollama server is offline at http://localhost:11434."
    }

def process_pdf(pdf_path: str, collection_name: str = "default_collection"):
    """Load PDF, split text into chunks with page numbers, and index into Chroma vector database."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Enrich metadata (source filename and 1-based page numbers)
    filename = os.path.basename(pdf_path)
    for doc in docs:
        doc.metadata["source"] = filename
        current_page = doc.metadata.get("page", 0)
        # Handle zero-indexed page numbers from PyPDFLoader
        doc.metadata["page"] = current_page + 1 if isinstance(current_page, int) else 1

    # 2. Split into chunks using Semantic Chunking
    from langchain_experimental.text_splitter import SemanticChunker
    
    embeddings = get_embeddings()
    text_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=95,
        number_of_chunks=None
    )
    splits = text_splitter.split_documents(docs)
    
    # Ensure each chunk is around 300 characters (adjust if needed)
    final_splits = []
    for doc in splits:
        content = doc.page_content
        if len(content) > 300:
            # Further split large semantic chunks to ~300 chars
            sub_chunks = []
            words = content.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                word_len = len(word) + 1  # +1 for space
                if current_length + word_len > 300 and current_chunk:
                    sub_chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = word_len
                else:
                    current_chunk.append(word)
                    current_length += word_len
            
            if current_chunk:
                sub_chunks.append(' '.join(current_chunk))
            
            # Create new documents for each sub-chunk
            for sub_chunk in sub_chunks:
                from langchain_core.documents import Document
                final_splits.append(Document(
                    page_content=sub_chunk,
                    metadata=doc.metadata.copy()
                ))
        else:
            final_splits.append(doc)
    
    splits = final_splits

    # 3. Embeddings & VectorStore
    embeddings = get_embeddings()
    
    db_dir = os.path.join(".", "chroma_db", collection_name)
    if os.path.exists(db_dir):
        try:
            shutil.rmtree(db_dir)
        except Exception:
            pass

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=db_dir,
        collection_name=collection_name
    )

    return vectorstore, len(splits), len(docs)

def query_rag_pipeline(
    vectorstore: Chroma,
    question: str,
    k: int = 4,
    temperature: float = 0.1,
    model_name: str = "phi3:mini"
) -> Dict[str, Any]:
    """Execute RAG query over vectorstore and format answer with retrieved chunks."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever.invoke(question)

    doc_sources = []
    for idx, doc in enumerate(retrieved_docs):
        doc_sources.append({
            "chunk_id": idx + 1,
            "content": doc.page_content,
            "page": doc.metadata.get("page", 1),
            "source": doc.metadata.get("source", "Document")
        })

    formatted_context = "\n\n".join(
        f"[Chunk {i+1} | Page {doc['page']}]: {doc['content']}"
        for i, doc in enumerate(doc_sources)
    )

    # Check Ollama
    ollama_check = check_ollama_status()
    if not ollama_check["available"]:
        fallback_answer = (
            f"**Note: Local Ollama service is currently offline or unreachable at `http://localhost:11434`.**\n\n"
            f"### Retrieved Context Summary for: *\"{question}\"*\n\n"
        ) + "\n\n".join(
            f"> **Page {doc['page']}**: {doc['content']}" for doc in doc_sources[:3]
        ) + "\n\n*To enable LLM synthesis, start Ollama locally using `ollama serve` and pull your model (e.g. `ollama run phi3:mini`).*"
        return {
            "answer": fallback_answer,
            "sources": doc_sources,
            "ollama_active": False,
            "message": "Ollama service offline. Displaying extracted semantic context."
        }

    # Ollama is available -> query model
    try:
        llm = ChatOllama(model=model_name, temperature=temperature)
        prompt = ChatPromptTemplate.from_template("""
You are an intelligent RAG assistant answering user questions based strictly on the provided document context.

Context:
{context}

Question: {question}

Instructions:
- Provide a clear, comprehensive, and well-structured answer in Markdown format.
- Mention specific page numbers referenced from the context whenever appropriate.
- If the context does not contain enough information to answer the question, state that clearly.
""")
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": formatted_context, "question": question})

        return {
            "answer": answer,
            "sources": doc_sources,
            "ollama_active": True,
            "message": "Success"
        }
    except Exception as e:
        fallback_answer = (
            f"**Ollama Query Warning**: Unable to invoke model `{model_name}` ({str(e)}).\n\n"
            f"### Extracted Relevant Document Context:\n"
        ) + "\n\n".join(f"• **(Page {doc['page']})**: {doc['content']}" for doc in doc_sources)
        return {
            "answer": fallback_answer,
            "sources": doc_sources,
            "ollama_active": True,
            "error": str(e)
        }