"""LLM generation with Ollama"""
import requests
from typing import Dict, Any, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import OLLAMA_BASE_URL, DEFAULT_MODEL, DEFAULT_TEMPERATURE

def check_ollama_status() -> Dict[str, Any]:
    """Check if Ollama service is running and list available models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [m.get("name") for m in models_data]
            return {
                "available": True,
                "models": model_names,
                "message": "Ollama server is active"
            }
    except Exception as e:
        pass
    
    return {
        "available": False,
        "models": [],
        "message": f"Ollama server is offline at {OLLAMA_BASE_URL}"
    }

def format_context(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into context string"""
    formatted_parts = []
    
    for idx, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        content = chunk.get("content", "")
        page = metadata.get("page", "?")
        source = metadata.get("source", "Document")
        
        formatted_parts.append(
            f"[Chunk {idx} | {source} | Page {page}]:\n{content}"
        )
    
    return "\n\n".join(formatted_parts)

def generate_answer(
    question: str,
    context_chunks: List[Dict[str, Any]],
    model_name: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE
) -> Dict[str, Any]:
    """
    Generate answer using Ollama LLM
    
    Returns:
        Dict with 'answer', 'sources', 'ollama_active'
    """
    # Check Ollama status
    ollama_status = check_ollama_status()
    
    # Format context
    formatted_context = format_context(context_chunks)
    
    # Prepare source information
    sources = []
    for idx, chunk in enumerate(context_chunks, 1):
        metadata = chunk.get("metadata", {})
        sources.append({
            "chunk_id": idx,
            "content": chunk.get("content", ""),
            "source": metadata.get("source", "Document"),
            "page": metadata.get("page", "?"),
            "score": chunk.get("rerank_score", chunk.get("hybrid_score", 0.0))
        })
    
    # If Ollama is not available, return context summary
    if not ollama_status["available"]:
        fallback_answer = (
            f"**Note: Local Ollama service is currently offline at `{OLLAMA_BASE_URL}`.**\n\n"
            f"### Retrieved Context for: *\"{question}\"*\n\n"
        )
        
        for source in sources[:3]:
            fallback_answer += f"> **{source['source']}, Page {source['page']}**: {source['content'][:200]}...\n\n"
        
        fallback_answer += "\n*To enable LLM synthesis, start Ollama locally using `ollama serve` and pull your model (e.g., `ollama run phi3:mini`).*"
        
        return {
            "answer": fallback_answer,
            "sources": sources,
            "ollama_active": False,
            "message": "Ollama service offline. Displaying extracted context."
        }
    
    # Ollama is available, generate answer
    try:
        llm = ChatOllama(model=model_name, temperature=temperature, base_url=OLLAMA_BASE_URL)
        
        prompt = ChatPromptTemplate.from_template("""You are RAGForge, a document question-answering assistant.

Answer ONLY using the provided context below. Do not use outside knowledge.

**Rules:**
1. Do not invent facts or use information not in the context
2. If the answer isn't in the context, say: "I couldn't find this information in the uploaded documents."
3. Cite the document name and page number when referencing information
4. Keep the answer concise but complete
5. Use Markdown formatting for clarity

**Context:**
{context}

**Question:** {question}

**Answer:**""")
        
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": formatted_context, "question": question})
        
        return {
            "answer": answer,
            "sources": sources,
            "ollama_active": True,
            "model": model_name,
            "message": "Success"
        }
    
    except Exception as e:
        # Fallback if LLM fails
        fallback_answer = (
            f"**Ollama Query Error**: Unable to invoke model `{model_name}` - {str(e)}\n\n"
            f"### Extracted Relevant Context:\n\n"
        )
        
        for source in sources[:3]:
            fallback_answer += f"• **{source['source']}, Page {source['page']}**: {source['content'][:200]}...\n\n"
        
        return {
            "answer": fallback_answer,
            "sources": sources,
            "ollama_active": True,
            "error": str(e),
            "message": f"LLM error: {str(e)}"
        }
