"""Tests for retrieval pipeline"""
import pytest
from app.rag.retriever import normalize_scores, hybrid_search

class TestScoreNormalization:
    """Test score normalization"""
    
    def test_normalize_empty_results(self):
        """Empty results should return empty list"""
        result = normalize_scores([])
        assert result == []
    
    def test_normalize_scores_basic(self):
        """Basic score normalization"""
        from langchain_core.documents import Document
        
        docs = [
            (Document(page_content="text1", metadata={"id": 1}), 10.0),
            (Document(page_content="text2", metadata={"id": 2}), 5.0),
        ]
        
        normalized = normalize_scores(docs)
        
        assert len(normalized) == 2
        assert normalized[0]["score"] == 1.0  # Max score normalized to 1
        assert normalized[1]["score"] == 0.5  # Half of max

class TestHybridSearch:
    """Test hybrid retrieval"""
    
    @pytest.mark.skip(reason="Requires ChromaDB and BM25 setup")
    def test_hybrid_search_integration(self):
        """Integration test for hybrid search"""
        # This would require full setup with test data
        pass
