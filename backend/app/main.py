"""RAGForge FastAPI Backend"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api import documents, chat
from app.security import check_rate_limit

# Get allowed origins from environment
ALLOWED_ORIGINS_RAW = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:8000,http://localhost:8000,*"
)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]

# Get allowed hosts from environment
ALLOWED_HOSTS_RAW = os.getenv(
    "ALLOWED_HOSTS",
    "*"
)
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_RAW.split(",") if host.strip()]

app = FastAPI(
    title="RAGForge Engine",
    version="2.0.0",
    description="Real RAG Architecture with Hybrid Retrieval, Reranking, and Local LLM",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Security: Trusted host middleware (only active if not allowing all hosts)
if "*" not in ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# Enable CORS with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

from fastapi import UploadFile, File

# Include API routers
app.include_router(documents.router)
app.include_router(chat.router)

# Include health/monitoring endpoints
from app.api import health
app.include_router(health.router)

# Legacy alias endpoints for backward compatibility
@app.post("/api/upload")
async def legacy_upload(file: UploadFile = File(...)):
    return await documents.upload_document(file)

@app.post("/api/select_document")
async def legacy_select_document():
    return {"status": "success", "message": "Document selection acknowledged"}

# Serve React frontend (built files)
_default_frontend = Path(__file__).parent.parent.parent / "frontend"
if not _default_frontend.exists():
    # Try adjacent frontend directory (e.g., in containerized flat layout)
    _alt_frontend = Path(__file__).parent.parent / "frontend"
    if _alt_frontend.exists():
        _default_frontend = _alt_frontend

FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", str(_default_frontend)))

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
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    app_target = "app.main:app" if (Path.cwd() / "app" / "main.py").exists() else "main:app"
    uvicorn.run(app_target, host=host, port=port, reload=True)

