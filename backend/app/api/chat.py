"""Chat and query API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.rag.pipeline import query_pipeline
from app.rag.generator import check_ollama_status
from app.database.metadata import get_metadata_store
from app.config import FINAL_TOP_K, DEFAULT_MODEL, DEFAULT_TEMPERATURE

router = APIRouter(prefix="/api", tags=["chat"])

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question")
    top_k: int = Field(default=FINAL_TOP_K, ge=1, le=20, description="Number of top chunks to retrieve")
    model_name: str = Field(default=DEFAULT_MODEL, description="Ollama model name")
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=1.0, description="LLM temperature")

class SourceChunk(BaseModel):
    chunk_id: int
    content: str
    source: str
    page: Any
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    ollama_active: bool
    model: Optional[str] = None
    message: str

class HealthResponse(BaseModel):
    status: str
    ollama: Dict[str, Any]
    documents: Dict[str, Any]

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check Ollama status
    ollama_info = check_ollama_status()
    
    # Check documents
    metadata_store = get_metadata_store()
    all_docs = metadata_store.get_all_documents()
    
    return HealthResponse(
        status="online",
        ollama=ollama_info,
        documents={
            "count": len(all_docs),
            "total_chunks": sum(doc.get("chunks", 0) for doc in all_docs)
        }
    )

@router.post("/chat", response_model=QueryResponse)
async def chat_query(payload: QueryRequest):
    """
    Process a user question and return an answer with sources
    
    Pipeline:
    1. Hybrid retrieval (semantic + BM25)
    2. Reranking with cross-encoder
    3. Answer generation with Ollama
    """
    # Check if any documents exist
    metadata_store = get_metadata_store()
    all_docs = metadata_store.get_all_documents()
    
    if not all_docs:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded. Please upload a PDF document first."
        )
    
    try:
        result = query_pipeline(
            question=payload.question,
            top_k=payload.top_k,
            model_name=payload.model_name,
            temperature=payload.temperature
        )
        
        # Convert sources to response model
        sources = [
            SourceChunk(
                chunk_id=src["chunk_id"],
                content=src["content"],
                source=src["source"],
                page=src["page"],
                score=src["score"]
            )
            for src in result.get("sources", [])
        ]
        
        return QueryResponse(
            answer=result.get("answer", ""),
            sources=sources,
            ollama_active=result.get("ollama_active", False),
            model=result.get("model"),
            message=result.get("message", "")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@router.post("/search")
async def search_documents(payload: QueryRequest):
    """
    Search documents without answer generation (retrieval only)
    
    Returns just the retrieved and reranked chunks
    """
    from app.rag.retriever import hybrid_search
    from app.rag.reranker import rerank_results
    
    metadata_store = get_metadata_store()
    all_docs = metadata_store.get_all_documents()
    
    if not all_docs:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded. Please upload a PDF document first."
        )
    
    try:
        # Hybrid retrieval
        candidates = hybrid_search(payload.question)
        
        # Rerank
        reranked = rerank_results(payload.question, candidates, top_k=payload.top_k)
        
        # Format response
        sources = []
        for idx, chunk in enumerate(reranked, 1):
            metadata = chunk.get("metadata", {})
            sources.append({
                "chunk_id": idx,
                "content": chunk.get("content", ""),
                "source": metadata.get("source", "Document"),
                "page": metadata.get("page", "?"),
                "score": chunk.get("rerank_score", 0.0),
                "hybrid_score": chunk.get("hybrid_score", 0.0)
            })
        
        return {
            "status": "success",
            "query": payload.question,
            "results": sources
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
