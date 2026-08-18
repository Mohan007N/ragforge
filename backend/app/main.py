"""RAGForge FastAPI Backend"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api import documents, chat

app = FastAPI(
    title="RAGForge Engine",
    version="2.0.0",
    description="Real RAG Architecture with Hybrid Retrieval, Reranking, and Local LLM"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(documents.router)
app.include_router(chat.router)

# Serve React frontend (built files)
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve React frontend"""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse({"message": "RAGForge API Backend Running. Frontend not built yet."})
    
    @app.get("/favicon.svg")
    async def serve_favicon():
        """Serve favicon"""
        favicon_path = FRONTEND_DIR / "favicon.svg"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        return JSONResponse({"message": "Favicon not found"})
    
    @app.get("/icons.svg")
    async def serve_icons():
        """Serve icons"""
        icons_path = FRONTEND_DIR / "icons.svg"
        if icons_path.exists():
            return FileResponse(icons_path)
        return JSONResponse({"message": "Icons not found"})
else:
    @app.get("/")
    async def root():
        """Root endpoint when frontend is not available"""
        return {
            "message": "RAGForge API Backend v2.0.0",
            "status": "online",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build' in react-frontend directory."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
