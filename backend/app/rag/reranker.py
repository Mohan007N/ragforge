"""Cross-encoder reranking for retrieval refinement"""
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from app.config import RERANKER_MODEL

# Global reranker instance
_reranker_instance = None

def get_reranker() -> CrossEncoder:
    """Get or create the singleton cross-encoder reranker"""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = CrossEncoder(RERANKER_MODEL)
    return _reranker_instance

def rerank_results(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Rerank candidate chunks using cross-encoder
    
    Args:
        query: The user's question
        candidates: List of dicts with 'content' and 'metadata'
        top_k: Number of top results to return
    
    Returns:
        Reranked list of candidates with 'rerank_score'
    """
    if not candidates:
        return []
    
    reranker = get_reranker()
    
    # Prepare pairs for reranking
    pairs = [[query, candidate["content"]] for candidate in candidates]
    
    # Get reranking scores
    scores = reranker.predict(pairs)
    
    # Attach scores to candidates
    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)
    
    # Sort by rerank score
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    
    # Return top k
    return reranked[:top_k]
