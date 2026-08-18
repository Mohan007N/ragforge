"""Document ingestion pipeline"""
import os
import hashlib
from pathlib import Path
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def generate_document_hash(file_path: str) -> str:
    """Generate SHA256 hash for a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def extract_pdf_text(pdf_path: str) -> Tuple[List[Document], int]:
    """
    Extract text from PDF with page metadata
    
    Returns:
        Tuple of (documents, num_pages)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    # Enrich metadata
    filename = os.path.basename(pdf_path)
    doc_hash = generate_document_hash(pdf_path)
    
    for doc in docs:
        doc.metadata["source"] = filename
        doc.metadata["document_id"] = doc_hash
        # Convert 0-indexed page to 1-indexed
        current_page = doc.metadata.get("page", 0)
        doc.metadata["page"] = current_page + 1 if isinstance(current_page, int) else 1
    
    return docs, len(docs)

def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    Split documents into chunks with metadata preservation
    
    Each chunk maintains:
    - document_id
    - filename (source)
    - page number
    - chunk_id
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    splits = text_splitter.split_documents(docs)
    
    # Add chunk IDs
    for idx, chunk in enumerate(splits):
        doc_id = chunk.metadata.get("document_id", "unknown")
        page = chunk.metadata.get("page", 0)
        chunk.metadata["chunk_id"] = f"{doc_id[:8]}_{page:03d}_{idx:04d}"
    
    return splits

def process_pdf_document(pdf_path: str) -> Tuple[List[Document], str, int, int]:
    """
    Full ingestion pipeline for a PDF document
    
    Returns:
        Tuple of (chunks, document_hash, num_pages, num_chunks)
    """
    # Extract text
    docs, num_pages = extract_pdf_text(pdf_path)
    
    # Generate hash
    doc_hash = generate_document_hash(pdf_path)
    
    # Chunk
    chunks = chunk_documents(docs)
    
    return chunks, doc_hash, num_pages, len(chunks)
