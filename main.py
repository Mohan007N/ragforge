import os
import shutil
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from rag_pipeline import process_pdf, query_rag_pipeline, check_ollama_status

app = FastAPI(title="RAGForge Engine", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session state for active vector database and active document
class ApplicationState:
    active_vectorstore = None
    active_doc_name: Optional[str] = None
    active_doc_pages: int = 0
    active_doc_chunks: int = 0

state = ApplicationState()

UPLOAD_DIR = os.path.join(".", "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryPayload(BaseModel):
    question: str
    k: int = 4
    temperature: float = 0.1
    model_name: str = "phi3:mini"

class SelectDocPayload(BaseModel):
    filename: str

@app.get("/api/health")
def get_health():
    ollama_info = check_ollama_status()
    return {
        "status": "online",
        "ollama": ollama_info,
        "active_document": {
            "name": state.active_doc_name,
            "pages": state.active_doc_pages,
            "chunks": state.active_doc_chunks,
            "is_indexed": state.active_vectorstore is not None
        }
    }

@app.get("/api/documents")
def list_documents():
    docs = []
    if os.path.exists(UPLOAD_DIR):
        for fname in os.listdir(UPLOAD_DIR):
            if fname.lower().endswith(".pdf"):
                fpath = os.path.join(UPLOAD_DIR, fname)
                size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
                docs.append({
                    "name": fname,
                    "size_mb": size_mb,
                    "is_active": (fname == state.active_doc_name)
                })
    return {"documents": docs}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Process and index PDF into vector DB
    try:
        collection_name = file.filename.replace(".", "_").replace(" ", "_")
        vectorstore, num_chunks, num_pages = process_pdf(file_path, collection_name)
        
        state.active_vectorstore = vectorstore
        state.active_doc_name = file.filename
        state.active_doc_pages = num_pages
        state.active_doc_chunks = num_chunks

        return {
            "status": "success",
            "message": f"Successfully processed and indexed '{file.filename}'",
            "document": {
                "name": file.filename,
                "pages": num_pages,
                "chunks": num_chunks
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@app.post("/api/select_document")
def select_document(payload: SelectDocPayload):
    file_path = os.path.join(UPLOAD_DIR, payload.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested document not found.")

    try:
        collection_name = payload.filename.replace(".", "_").replace(" ", "_")
        vectorstore, num_chunks, num_pages = process_pdf(file_path, collection_name)
        
        state.active_vectorstore = vectorstore
        state.active_doc_name = payload.filename
        state.active_doc_pages = num_pages
        state.active_doc_chunks = num_chunks

        return {
            "status": "success",
            "message": f"Switched active document to '{payload.filename}'",
            "document": {
                "name": payload.filename,
                "pages": num_pages,
                "chunks": num_chunks
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing selected document: {str(e)}")

@app.post("/api/query")
def query_doc(payload: QueryPayload):
    if state.active_vectorstore is None:
        # Check if there are any documents in data/ and auto-load the first one
        doc_files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(".pdf")] if os.path.exists(UPLOAD_DIR) else []
        if doc_files:
            file_path = os.path.join(UPLOAD_DIR, doc_files[0])
            collection_name = doc_files[0].replace(".", "_").replace(" ", "_")
            vectorstore, num_chunks, num_pages = process_pdf(file_path, collection_name)
            state.active_vectorstore = vectorstore
            state.active_doc_name = doc_files[0]
            state.active_doc_pages = num_pages
            state.active_doc_chunks = num_chunks
        else:
            raise HTTPException(status_code=400, detail="No document uploaded or selected. Please upload a PDF first.")

    try:
        result = query_rag_pipeline(
            vectorstore=state.active_vectorstore,
            question=payload.question,
            k=payload.k,
            temperature=payload.temperature,
            model_name=payload.model_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

# Serve Static Frontend
FRONTEND_DIR = os.path.join(".", "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "RAGForge API Backend Running. Frontend coming soon."})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

