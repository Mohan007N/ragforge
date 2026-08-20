# ==========================================================
# RAGForge Unified - All-in-One Production Dockerfile
# Stage 1: Build Vite React Frontend
# Stage 2: Python 3.11 Backend serving API & Frontend Assets
# Ideal for single-container PaaS (Render, Railway, Fly.io, Cloud Run)
# ==========================================================

# ----------------- Stage 1: Frontend Build -----------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build/react-frontend

COPY react-frontend/package.json react-frontend/package-lock.json ./
RUN npm ci

COPY react-frontend/ .
RUN npm run build

# ----------------- Stage 2: Production Backend & Unified Server -----------------
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=2 \
    FRONTEND_DIR=/app/frontend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create non-root user and persistent directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/documents /app/storage/chroma /app/storage/bm25 /app/frontend && \
    chown -R appuser:appuser /app

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /build/frontend /app/frontend

# Copy backend code
COPY backend/app/ /app/app/

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Production ASGI server running with Gunicorn & Uvicorn workers
CMD ["sh", "-c", "exec gunicorn -k uvicorn.workers.UvicornWorker -b ${HOST}:${PORT} --workers ${WORKERS:-2} --timeout 120 --access-logfile - --error-logfile - app.main:app"]
