"""Pytest configuration and fixtures"""
import os
import sys
import pytest
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def sample_pdf_path():
    """Path to sample test PDF"""
    test_dir = Path(__file__).parent
    return test_dir / "fixtures" / "sample.pdf"

@pytest.fixture
def mock_document_data():
    """Mock document metadata"""
    return {
        "document_id": "test123abc",
        "filename": "test_document.pdf",
        "pages": 5,
        "chunks": 25,
        "file_size_mb": 1.2
    }
