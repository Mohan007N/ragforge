# ==========================================================
# RAGForge Backend - Production Dockerfile
# Python 3.11 Slim with Multi-Worker Gunicorn/Uvicorn ASGI
# ==========================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=2

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching layers
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create non-root user and persistent storage directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/documents /app/storage/chroma /app/storage/bm25 && \
    chown -R appuser:appuser /app

# Copy application source code
COPY app/ ./app/

# Switch to non-root user
USER appuser

# Expose backend API port
EXPOSE 8000

# Health check to ensure service readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start production ASGI server with Gunicorn + Uvicorn workers
CMD ["sh", "-c", "exec gunicorn -k uvicorn.workers.UvicornWorker -b ${HOST}:${PORT} --workers ${WORKERS:-2} --timeout 120 --access-logfile - --error-logfile - app.main:app"]
