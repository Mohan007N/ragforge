"""Tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Health endpoint should return status"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "ollama" in data
        assert "documents" in data

class TestDocumentEndpoints:
    """Test document management endpoints"""
    
    def test_list_documents(self, client):
        """List documents should return array"""
        response = client.get("/api/documents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    @pytest.mark.skip(reason="Requires file upload setup")
    def test_upload_document(self, client):
        """Upload document endpoint"""
        # Would need actual PDF file for full test
        pass

class TestChatEndpoints:
    """Test chat endpoints"""
    
    @pytest.mark.skip(reason="Requires indexed documents")
    def test_chat_query(self, client):
        """Chat endpoint should accept queries"""
        response = client.post(
            "/api/chat",
            json={"question": "What is machine learning?"}
        )
        
        # Without documents, should return appropriate message
        assert response.status_code in [200, 400]
