"""Configuration for RAGForge"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "documents"
STORAGE_DIR = BASE_DIR / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma"
BM25_DIR = STORAGE_DIR / "bm25"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
BM25_DIR.mkdir(parents=True, exist_ok=True)

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# Chunking parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# Retrieval parameters
SEMANTIC_TOP_K = int(os.getenv("SEMANTIC_TOP_K", "10"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "10"))
HYBRID_WEIGHT_SEMANTIC = float(os.getenv("HYBRID_WEIGHT_SEMANTIC", "0.6"))
HYBRID_WEIGHT_BM25 = float(os.getenv("HYBRID_WEIGHT_BM25", "0.4"))
FINAL_TOP_K = int(os.getenv("FINAL_TOP_K", "5"))

# Reranker model
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# LLM parameters
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "phi3:mini")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))

# ChromaDB collection
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ragforge_documents")

