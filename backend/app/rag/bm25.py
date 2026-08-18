"""BM25 keyword search implementation"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.config import BM25_DIR

BM25_INDEX_PATH = BM25_DIR / "bm25_index.pkl"
BM25_METADATA_PATH = BM25_DIR / "bm25_metadata.json"

class BM25Index:
    """BM25 index for keyword-based retrieval"""
    
    def __init__(self):
        self.bm25 = None
        self.chunks = []
        self.load()
    
    def load(self):
        """Load existing BM25 index from disk"""
        if BM25_INDEX_PATH.exists() and BM25_METADATA_PATH.exists():
            try:
                with open(BM25_INDEX_PATH, 'rb') as f:
                    self.bm25 = pickle.load(f)
                
                with open(BM25_METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"Error loading BM25 index: {e}")
                self.bm25 = None
                self.chunks = []
    
    def save(self):
        """Save BM25 index to disk"""
        try:
            with open(BM25_INDEX_PATH, 'wb') as f:
                pickle.dump(self.bm25, f)
            
            with open(BM25_METADATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f)
        except Exception as e:
            print(f"Error saving BM25 index: {e}")
    
    def build(self, documents: List[Document]):
        """Build BM25 index from documents"""
        # Tokenize documents
        self.chunks = []
        tokenized_corpus = []
        
        for doc in documents:
            chunk_data = {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            self.chunks.append(chunk_data)
            
            # Simple whitespace tokenization
            tokens = doc.page_content.lower().split()
            tokenized_corpus.append(tokens)
        
        # Build BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.save()
    
    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search using BM25
        
        Returns:
            List of dicts with 'content', 'metadata', and 'score'
        """
        if not self.bm25 or not self.chunks:
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                results.append({
                    "content": self.chunks[idx]["content"],
                    "metadata": self.chunks[idx]["metadata"],
                    "score": float(scores[idx])
                })
        
        return results
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to existing index"""
        # For simplicity, rebuild the entire index
        # In production, you'd want incremental updates
        all_docs = []
        
        # Convert existing chunks back to Documents
        for chunk in self.chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
            all_docs.append(doc)
        
        # Add new documents
        all_docs.extend(documents)
        
        # Rebuild
        self.build(all_docs)
    
    def delete_document(self, document_id: str):
        """Delete all chunks belonging to a document"""
        if not self.chunks:
            return 0
        
        # Filter out chunks from this document
        filtered_chunks = [
            chunk for chunk in self.chunks
            if chunk["metadata"].get("document_id") != document_id
        ]
        
        deleted_count = len(self.chunks) - len(filtered_chunks)
        
        if deleted_count > 0:
            # Rebuild index with remaining chunks
            remaining_docs = [
                Document(page_content=chunk["content"], metadata=chunk["metadata"])
                for chunk in filtered_chunks
            ]
            self.build(remaining_docs)
        
        return deleted_count

# Global BM25 index instance
_bm25_instance = None

def get_bm25_index() -> BM25Index:
    """Get or create the singleton BM25 index"""
    global _bm25_instance
    if _bm25_instance is None:
        _bm25_instance = BM25Index()
    return _bm25_instance

def bm25_search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    """Perform BM25 keyword search"""
    index = get_bm25_index()
    return index.search(query, k=k)
