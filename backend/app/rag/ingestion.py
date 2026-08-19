"""Document ingestion pipeline"""
import os
import hashlib
import logging
from pathlib import Path
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def generate_document_hash(file_path: str) -> str:
    """Generate SHA256 hash for a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def _is_valid_text(text: str) -> bool:
    """Check if text content is non-empty and contains meaningful characters.
    
    Filters out blank pages, whitespace-only content, and strings too short
    to embed (which would cause TextEncodeInput errors in HuggingFace tokenizer).
    """
    if not text or not isinstance(text, str):
        return False
    stripped = text.strip()
    # Must have at least some real content (not just whitespace/punctuation)
    return len(stripped) > 0

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
    total_pages = len(docs)
    
    # Enrich metadata
    filename = os.path.basename(pdf_path)
    doc_hash = generate_document_hash(pdf_path)
    
    valid_docs = []
    for doc in docs:
        doc.metadata["source"] = filename
        doc.metadata["document_id"] = doc_hash
        # Convert 0-indexed page to 1-indexed
        current_page = doc.metadata.get("page", 0)
        doc.metadata["page"] = current_page + 1 if isinstance(current_page, int) else 1
        
        # Filter out blank/empty pages to prevent TextEncodeInput errors
        if _is_valid_text(doc.page_content):
            valid_docs.append(doc)
        else:
            logger.info(f"Skipping blank page {doc.metadata['page']} in {filename}")
    
    if not valid_docs:
        raise ValueError(
            f"No extractable text found in '{filename}'. "
            f"The PDF may contain only images or scanned content ({total_pages} pages scanned)."
        )
    
    logger.info(f"Extracted text from {len(valid_docs)}/{total_pages} pages in {filename}")
    return valid_docs, total_pages

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
    
    # Filter out any empty chunks produced by the splitter at boundaries
    valid_splits = [chunk for chunk in splits if _is_valid_text(chunk.page_content)]
    
    if len(valid_splits) < len(splits):
        logger.info(f"Filtered out {len(splits) - len(valid_splits)} empty chunks from text splitting")
    
    # Add chunk IDs
    for idx, chunk in enumerate(valid_splits):
        doc_id = chunk.metadata.get("document_id", "unknown")
        page = chunk.metadata.get("page", 0)
        chunk.metadata["chunk_id"] = f"{doc_id[:8]}_{page:03d}_{idx:04d}"
    
    return valid_splits

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
    
    if not chunks:
        raise ValueError(
            f"Document produced 0 valid chunks after processing. "
            f"The text content may be too short or contain only non-textual data."
        )
    
    return chunks, doc_hash, num_pages, len(chunks)
