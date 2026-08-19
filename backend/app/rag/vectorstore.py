"""ChromaDB vector store management"""
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config import CHROMA_DIR, CHROMA_COLLECTION_NAME
from app.rag.embeddings import get_embeddings

def get_vectorstore() -> Chroma:
    """Get or create the persistent ChromaDB vectorstore"""
    embeddings = get_embeddings()
    
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    return vectorstore

def add_documents_to_vectorstore(chunks: List[Document]) -> int:
    """
    Add document chunks to the vector store
    
    Returns:
        Number of chunks added
    """
    # Safety filter: remove any chunks with empty/whitespace-only content
    # to prevent TextEncodeInput errors in the HuggingFace tokenizer
    valid_chunks = [
        chunk for chunk in chunks 
        if chunk.page_content and chunk.page_content.strip()
    ]
    
    if not valid_chunks:
        return 0
    
    vectorstore = get_vectorstore()
    vectorstore.add_documents(valid_chunks)
    return len(valid_chunks)

def semantic_search(query: str, k: int = 10) -> List[tuple]:
    """
    Perform semantic search using vector similarity
    
    Returns:
        List of (Document, score) tuples
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results

def delete_document_from_vectorstore(document_id: str):
    """Delete all chunks belonging to a document"""
    vectorstore = get_vectorstore()
    
    # Query for all chunks with this document_id
    collection = vectorstore._collection
    results = collection.get(where={"document_id": document_id})
    
    if results and results['ids']:
        collection.delete(ids=results['ids'])
        return len(results['ids'])
    
    return 0
