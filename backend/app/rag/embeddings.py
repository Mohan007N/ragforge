"""Embedding model management"""
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL, EMBEDDING_DEVICE

# Global cached embedding model
_embeddings_instance = None

def get_embeddings():
    """Get or create the singleton embedding model instance"""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": EMBEDDING_DEVICE}
        )
    return _embeddings_instance
