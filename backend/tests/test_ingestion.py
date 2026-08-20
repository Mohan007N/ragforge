"""Tests for document ingestion pipeline"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document
from app.rag.ingestion import (
    generate_document_hash,
    _is_valid_text,
    chunk_documents
)

class TestDocumentHash:
    """Test document hashing"""
    
    def test_generate_hash_consistent(self, tmp_path):
        """Same file should produce same hash"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        hash1 = generate_document_hash(str(test_file))
        hash2 = generate_document_hash(str(test_file))
        
        assert hash1 == hash2
    
    def test_generate_hash_different_files(self, tmp_path):
        """Different files should produce different hashes"""
        file1 = tmp_path / "test1.txt"
        file2 = tmp_path / "test2.txt"
        
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        hash1 = generate_document_hash(str(file1))
        hash2 = generate_document_hash(str(file2))
        
        assert hash1 != hash2

class TestTextValidation:
    """Test text validation"""
    
    def test_valid_text(self):
        """Valid text should pass"""
        assert _is_valid_text("This is valid text")
        assert _is_valid_text("123 numbers are valid")
    
    def test_invalid_text(self):
        """Invalid text should fail"""
        assert not _is_valid_text("")
        assert not _is_valid_text("   ")
        assert not _is_valid_text(None)

class TestChunking:
    """Test document chunking"""
    
    def test_chunk_documents_basic(self):
        """Basic chunking should work"""
        docs = [
            Document(
                page_content="This is a test document with some content.",
                metadata={"document_id": "test123", "source": "test.pdf", "page": 1}
            )
        ]
        
        chunks = chunk_documents(docs)
        
        assert len(chunks) > 0
        assert all(c.metadata.get("chunk_id") for c in chunks)
        assert all(c.metadata.get("document_id") == "test123" for c in chunks)
    
    def test_chunk_metadata_preservation(self):
        """Chunking should preserve metadata"""
        docs = [
            Document(
                page_content="Test content " * 100,
                metadata={"document_id": "abc123", "source": "doc.pdf", "page": 2}
            )
        ]
        
        chunks = chunk_documents(docs)
        
        for chunk in chunks:
            assert chunk.metadata["document_id"] == "abc123"
            assert chunk.metadata["source"] == "doc.pdf"
            assert chunk.metadata["page"] == 2
            assert "chunk_id" in chunk.metadata
