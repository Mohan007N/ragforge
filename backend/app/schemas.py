"""Pydantic schemas for API documentation"""
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    """Document metadata schema"""
    document_id: str = Field(..., description="Unique document identifier (SHA256 hash)")
    filename: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages in document", ge=1)
    chunks: int = Field(..., description="Number of text chunks", ge=1)
    file_size_mb: float = Field(..., description="File size in megabytes", ge=0)
    upload_date: Optional[str] = Field(None, description="ISO format upload timestamp")

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    status: str = Field(..., description="Upload status", example="success")
    message: str = Field(..., description="Status message")
    document: DocumentMetadata

class DocumentListResponse(BaseModel):
    """Response for document list"""
    documents: List[DocumentMetadata] = Field(..., description="List of all documents")

class SourceChunk(BaseModel):
    """Retrieved source chunk"""
    chunk_id: int = Field(..., description="Chunk number in response")
    content: str = Field(..., description="Chunk text content")
    page: int = Field(..., description="Source page number")
    source: str = Field(..., description="Source document filename")
    score: Optional[float] = Field(None, description="Relevance score")

class ChatRequest(BaseModel):
    """Chat query request"""
    question: str = Field(..., description="User question", min_length=1, max_length=5000)
    top_k: int = Field(5, description="Number of chunks to retrieve", ge=1, le=20)
    model_name: str = Field("phi3:mini", description="LLM model name")
    temperature: float = Field(0.1, description="LLM temperature", ge=0, le=2)

class ChatResponse(BaseModel):
    """Chat query response"""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceChunk] = Field(..., description="Retrieved source chunks")
    ollama_active: bool = Field(..., description="Whether Ollama LLM was used")
    message: Optional[str] = Field(None, description="Status message")

class SearchRequest(BaseModel):
    """Search-only request (no LLM generation)"""
    question: str = Field(..., description="Search query", min_length=1, max_length=5000)
    top_k: int = Field(5, description="Number of results", ge=1, le=20)

class SearchResponse(BaseModel):
    """Search results"""
    results: List[SourceChunk] = Field(..., description="Retrieved chunks")
    count: int = Field(..., description="Number of results")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="System status", example="online")
    ollama: dict = Field(..., description="Ollama service status")
    documents: dict = Field(..., description="Document statistics")

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str = Field(..., description="Error message")
