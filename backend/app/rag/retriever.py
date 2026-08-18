"""Hybrid retrieval combining semantic and keyword search"""
from typing import List, Dict, Any
from app.rag.vectorstore import semantic_search
from app.rag.bm25 import bm25_search
from app.config import (
    SEMANTIC_TOP_K,
    BM25_TOP_K,
    HYBRID_WEIGHT_SEMANTIC,
    HYBRID_WEIGHT_BM25
)

def normalize_scores(results: List[tuple], max_score: float = None) -> List[Dict[str, Any]]:
    """Normalize scores to 0-1 range"""
    if not results:
        return []
    
    if max_score is None:
        scores = [score for _, score in results]
        max_score = max(scores) if scores else 1.0
    
    if max_score == 0:
        max_score = 1.0
    
    normalized = []
    for item, score in results:
        normalized.append({
            "content": item.page_content if hasattr(item, 'page_content') else item.get("content"),
            "metadata": item.metadata if hasattr(item, 'metadata') else item.get("metadata"),
            "score": score / max_score
        })
    
    return normalized

def hybrid_search(query: str, semantic_k: int = SEMANTIC_TOP_K, bm25_k: int = BM25_TOP_K) -> List[Dict[str, Any]]:
    """
    Perform hybrid search combining semantic and keyword retrieval
    
    Returns:
        List of dicts with 'content', 'metadata', and 'hybrid_score'
    """
    # Get semantic results
    semantic_results = semantic_search(query, k=semantic_k)
    
    # Get BM25 results
    bm25_results = bm25_search(query, k=bm25_k)
    
    # Normalize scores
    # For ChromaDB, lower distance = better, so we invert
    semantic_normalized = []
    if semantic_results:
        for doc, distance in semantic_results:
            # Convert distance to similarity (higher is better)
            similarity = 1 / (1 + distance)
            semantic_normalized.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": similarity
            })
        
        # Normalize to 0-1
        max_score = max(r["score"] for r in semantic_normalized)
        if max_score > 0:
            for r in semantic_normalized:
                r["score"] = r["score"] / max_score
    
    # Normalize BM25 scores
    bm25_normalized = []
    if bm25_results:
        max_score = max(r["score"] for r in bm25_results)
        if max_score > 0:
            for r in bm25_results:
                bm25_normalized.append({
                    "content": r["content"],
                    "metadata": r["metadata"],
                    "score": r["score"] / max_score
                })
    
    # Combine results using chunk_id as key
    combined = {}
    
    for result in semantic_normalized:
        chunk_id = result["metadata"].get("chunk_id", "")
        combined[chunk_id] = {
            "content": result["content"],
            "metadata": result["metadata"],
            "semantic_score": result["score"],
            "bm25_score": 0.0
        }
    
    for result in bm25_normalized:
        chunk_id = result["metadata"].get("chunk_id", "")
        if chunk_id in combined:
            combined[chunk_id]["bm25_score"] = result["score"]
        else:
            combined[chunk_id] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "semantic_score": 0.0,
                "bm25_score": result["score"]
            }
    
    # Calculate hybrid scores
    hybrid_results = []
    for chunk_id, data in combined.items():
        hybrid_score = (
            HYBRID_WEIGHT_SEMANTIC * data["semantic_score"] +
            HYBRID_WEIGHT_BM25 * data["bm25_score"]
        )
        
        hybrid_results.append({
            "content": data["content"],
            "metadata": data["metadata"],
            "hybrid_score": hybrid_score,
            "semantic_score": data["semantic_score"],
            "bm25_score": data["bm25_score"]
        })
    
    # Sort by hybrid score
    hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    
    return hybrid_results
