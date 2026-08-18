"""Document metadata storage (simple JSON-based for now)"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import STORAGE_DIR

METADATA_FILE = STORAGE_DIR / "documents_metadata.json"

class DocumentMetadataStore:
    """Simple JSON-based metadata store for documents"""
    
    def __init__(self):
        self.metadata_file = METADATA_FILE
        self.documents = self.load()
    
    def load(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return {}
    
    def save(self):
        """Save metadata to disk"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def add_document(self, document_id: str, filename: str, pages: int, chunks: int, file_size: int):
        """Add document metadata"""
        self.documents[document_id] = {
            "document_id": document_id,
            "filename": filename,
            "pages": pages,
            "chunks": chunks,
            "file_size_bytes": file_size,
            "uploaded_at": datetime.now().isoformat(),
            "status": "indexed"
        }
        self.save()
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        return self.documents.get(document_id)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents metadata"""
        return list(self.documents.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document metadata"""
        if document_id in self.documents:
            del self.documents[document_id]
            self.save()
            return True
        return False
    
    def document_exists(self, document_id: str) -> bool:
        """Check if document exists"""
        return document_id in self.documents

# Global metadata store instance
_metadata_store = None

def get_metadata_store() -> DocumentMetadataStore:
    """Get or create the singleton metadata store"""
    global _metadata_store
    if _metadata_store is None:
        _metadata_store = DocumentMetadataStore()
    return _metadata_store
