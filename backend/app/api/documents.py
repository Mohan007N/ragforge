"""Document management API endpoints"""
import os
import logging
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from app.config import DATA_DIR
from app.rag.pipeline import ingest_document, delete_document
from app.rag.ingestion import generate_document_hash
from app.database.metadata import get_metadata_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int
    file_size_mb: float
    uploaded_at: str
    status: str

class DeleteDocumentRequest(BaseModel):
    document_id: str

@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    """List all uploaded documents"""
    metadata_store = get_metadata_store()
    documents = metadata_store.get_all_documents()
    
    response = []
    for doc in documents:
        response.append(DocumentResponse(
            document_id=doc["document_id"],
            filename=doc["filename"],
            pages=doc["pages"],
            chunks=doc["chunks"],
            file_size_mb=round(doc["file_size_bytes"] / (1024 * 1024), 2),
            uploaded_at=doc["uploaded_at"],
            status=doc["status"]
        ))
    
    return response

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a PDF document"""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported. Please upload a .pdf file.")
    
    # Save file
    file_path = DATA_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved file: {file.filename} ({os.path.getsize(file_path)} bytes)")
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Generate document hash
    doc_hash = generate_document_hash(str(file_path))
    
    # Check if document already exists
    metadata_store = get_metadata_store()
    if metadata_store.document_exists(doc_hash):
        return {
            "status": "already_exists",
            "message": f"Document '{file.filename}' is already indexed",
            "document_id": doc_hash
        }
    
    # Ingest document
    try:
        result = ingest_document(str(file_path))
        
        # Store metadata
        file_size = os.path.getsize(file_path)
        metadata_store.add_document(
            document_id=result["document_id"],
            filename=result["filename"],
            pages=result["pages"],
            chunks=result["chunks"],
            file_size=file_size
        )
        
        logger.info(f"Successfully indexed {file.filename}: {result['pages']} pages, {result['chunks']} chunks")
        
        return {
            "status": "success",
            "message": f"Successfully processed and indexed '{file.filename}'",
            "document": result
        }
    
    except ValueError as e:
        # Content-related issues (e.g., no extractable text, image-only PDF)
        logger.warning(f"Content error processing {file.filename}: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Clean up file if ingestion fails
        logger.error(f"Failed to index {file.filename}: {e}", exc_info=True)
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document_endpoint(document_id: str):
    """Delete a document and all its chunks"""
    metadata_store = get_metadata_store()
    
    # Check if document exists
    doc_metadata = metadata_store.get_document(document_id)
    if not doc_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from indexes
        result = delete_document(document_id)
        
        # Delete metadata
        metadata_store.delete_document(document_id)
        
        # Delete physical file
        file_path = DATA_DIR / doc_metadata["filename"]
        if file_path.exists():
            file_path.unlink()
        
        return {
            "status": "success",
            "message": f"Successfully deleted document '{doc_metadata['filename']}'",
            "deletion_stats": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/{document_id}")
async def get_document_details(document_id: str):
    """Get detailed information about a document"""
    metadata_store = get_metadata_store()
    doc_metadata = metadata_store.get_document(document_id)
    
    if not doc_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc_metadata
