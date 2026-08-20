"""Health check and monitoring endpoints"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import requests
from app.security import verify_api_key
from app.monitoring import metrics, get_system_metrics, get_storage_metrics
from app.database.metadata import get_metadata_store
from app.config import OLLAMA_BASE_URL

router = APIRouter(prefix="/api", tags=["health"])

def check_ollama_status() -> Dict[str, Any]:
    """Check if Ollama service is active and list available models."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [m.get("name") for m in models_data]
            return {
                "available": True,
                "models": model_names,
                "message": "Ollama server is active."
            }
    except Exception:
        pass
    return {
        "available": False,
        "models": [],
        "message": f"Ollama server is offline at {OLLAMA_BASE_URL}."
    }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns system status, Ollama availability, and document count
    """
    ollama_status = check_ollama_status()
    metadata_store = get_metadata_store()
    documents = metadata_store.get_all_documents()
    
    total_chunks = sum(
        doc.get("chunks", 0) 
        for doc in documents
    )
    
    return {
        "status": "online",
        "ollama": ollama_status,
        "documents": {
            "count": len(documents),
            "total_chunks": total_chunks
        }
    }

@router.get("/metrics")
async def get_metrics(auth: bool = Depends(verify_api_key)) -> Dict[str, Any]:
    """
    Get application metrics (requires authentication)
    
    Returns:
        - Request counts and latencies
        - Error counts
        - System resources (CPU, memory, disk)
        - Storage usage
    """
    app_metrics = metrics.get_metrics()
    system_metrics = get_system_metrics()
    storage_metrics = get_storage_metrics()
    
    return {
        "application": app_metrics,
        "system": system_metrics,
        "storage": storage_metrics
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe
    
    Checks if application is ready to serve traffic
    """
    try:
        # Check if embedding model is loaded
        from app.rag.embeddings import get_embeddings
        embeddings = get_embeddings()
        
        # Check if ChromaDB is accessible
        from app.rag.vectorstore import get_vectorstore
        vectorstore = get_vectorstore()
        
        return {
            "ready": True,
            "checks": {
                "embeddings": True,
                "vectorstore": True
            }
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e)
        }

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes-style liveness probe
    
    Simple check that the application is running
    """
    return {"status": "alive"}
