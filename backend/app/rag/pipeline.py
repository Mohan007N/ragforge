"""Complete RAG Pipeline"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from app.rag.ingestion import process_pdf_document
from app.rag.vectorstore import add_documents_to_vectorstore, delete_document_from_vectorstore
from app.rag.bm25 import get_bm25_index
from app.rag.retriever import hybrid_search
from app.rag.reranker import rerank_results
from app.rag.generator import generate_answer
from app.config import FINAL_TOP_K, DEFAULT_MODEL, DEFAULT_TEMPERATURE

def ingest_document(pdf_path: str) -> Dict[str, Any]:
    """
    Complete document ingestion pipeline
    
    Steps:
    1. Extract PDF text
    2. Generate document hash
    3. Chunk into segments
    4. Add to ChromaDB (semantic)
    5. Add to BM25 index (keyword)
    
    Returns:
        Dict with document metadata and statistics
    """
    # Process PDF
    chunks, doc_hash, num_pages, num_chunks = process_pdf_document(pdf_path)
    
    # Add to vector store
    add_documents_to_vectorstore(chunks)
    
    # Add to BM25 index
    bm25_index = get_bm25_index()
    bm25_index.add_documents(chunks)
    
    return {
        "document_id": doc_hash,
        "filename": chunks[0].metadata.get("source", "unknown"),
        "pages": num_pages,
        "chunks": num_chunks,
        "status": "indexed"
    }

def query_pipeline(
    question: str,
    top_k: int = FINAL_TOP_K,
    model_name: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE
) -> Dict[str, Any]:
    """
    Complete RAG query pipeline
    
    Steps:
    1. Perform hybrid retrieval (semantic + BM25)
    2. Rerank candidates with cross-encoder
    3. Select top-k chunks
    4. Generate answer with Ollama
    
    Returns:
        Dict with answer and sources
    """
    # Step 1: Hybrid retrieval
    candidates = hybrid_search(question)
    
    if not candidates:
        return {
            "answer": "No relevant documents found. Please upload documents first.",
            "sources": [],
            "ollama_active": False,
            "message": "No documents in database"
        }
    
    # Step 2: Rerank
    reranked = rerank_results(question, candidates, top_k=top_k)
    
    # Step 3: Generate answer
    result = generate_answer(
        question=question,
        context_chunks=reranked,
        model_name=model_name,
        temperature=temperature
    )
    
    return result

def delete_document(document_id: str) -> Dict[str, Any]:
    """
    Delete document from all indexes
    
    Returns:
        Dict with deletion statistics
    """
    # Delete from vector store
    chroma_deleted = delete_document_from_vectorstore(document_id)
    
    # Delete from BM25 index
    bm25_index = get_bm25_index()
    bm25_deleted = bm25_index.delete_document(document_id)
    
    return {
        "document_id": document_id,
        "chunks_deleted_chroma": chroma_deleted,
        "chunks_deleted_bm25": bm25_deleted,
        "status": "deleted"
    }
