# RAGForge v2.0 - Real RAG Architecture

<RAGForge - Local Document Q&A with Hybrid Retrieval, Reranking, and Local LLM

## Architecture Overview

```
┌─────────────────────┐
│   React Frontend    │
│      (Vite)         │
└──────────┬──────────┘
           │ REST/HTTP
┌──────────▼──────────┐
│   FastAPI Backend   │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ ChromaDB│   │  BM25  │
│(Semantic)   │(Keyword)│
└────┬───┘   └────┬───┘
     │            │
     └─────┬──────┘
           ▼
     Hybrid Fusion
           │
           ▼
      Reranker
  (Cross-Encoder)
           │
           ▼
     Top-K Context
           │
           ▼
    Ollama (phi3:mini)
           │
           ▼
   Grounded Answer
     + Citations
```

## Features

✨ **Full RAG Pipeline**
- PDF text extraction and intelligent chunking
- Document hash-based deduplication
- Metadata preservation (page numbers, source files)

🔍 **Hybrid Retrieval**
- **Semantic search**: Dense vectors with sentence-transformers
- **Keyword search**: BM25 for exact term matching
- **Fusion scoring**: 60% semantic + 40% BM25

🎯 **Reranking**
- Cross-encoder reranking (`ms-marco-MiniLM-L-6-v2`)
- Dramatically improves retrieval precision

🤖 **Local LLM Generation**
- Ollama integration with phi3:mini
- Strict context-only answering (reduced hallucination)
- Page-level source citations

📦 **Document Management**
- Upload multiple PDFs
- View chunking statistics
- Delete documents with full cleanup

🎨 **Modern React UI**
- Real-time chat interface
- Source citations with expandable chunks
- Health monitoring dashboard

## Project Structure

```
ragforge/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── api/
│   │   │   ├── chat.py          # Chat API endpoints
│   │   │   └── documents.py     # Document management API
│   │   ├── rag/
│   │   │   ├── ingestion.py     # PDF processing & chunking
│   │   │   ├── embeddings.py    # Embedding model management
│   │   │   ├── vectorstore.py   # ChromaDB integration
│   │   │   ├── bm25.py          # BM25 keyword search
│   │   │   ├── retriever.py     # Hybrid retrieval
│   │   │   ├── reranker.py      # Cross-encoder reranking
│   │   │   ├── generator.py     # LLM generation
│   │   │   └── pipeline.py      # Complete RAG pipeline
│   │   └── database/
│   │       └── metadata.py      # Document metadata store
│   ├── data/documents/          # Uploaded PDFs
│   ├── storage/
│   │   ├── chroma/              # Vector database
│   │   └── bm25/                # BM25 index
│   ├── requirements.txt
│   └── .env
├── react-frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── ChatArea.jsx
│   │   ├── Sidebar.jsx
│   │   └── api.js
│   └── package.json
└── README.md
```

## Installation & Setup

### Prerequisites

1. **Python 3.11+**
2. **Node.js 18+**
3. **Ollama** (for local LLM)

### Step 1: Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com)

Pull the phi3:mini model:
```bash
ollama pull phi3:mini
```

Verify Ollama is running:
```bash
ollama list
```

### Step 2: Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (if not exists):
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
.\\venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI + Uvicorn
- LangChain with Chroma, HuggingFace, and Ollama integrations
- sentence-transformers for embeddings and reranking
- rank-bm25 for keyword search
- pypdf for PDF processing

### Step 3: Frontend Setup

1. Navigate to react-frontend directory:
```bash
cd react-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Build frontend for production:
```bash
npm run build
```

This builds the React app and outputs to `frontend/` directory which the backend serves.

### Step 4: Run the Application

1. Start the backend server:
```bash
cd backend
python app/main.py
```

The server will start on `http://127.0.0.1:8000`

2. Open your browser and navigate to:
```
http://127.0.0.1:8000
```

## Development Mode

For frontend development with hot reload:

```bash
cd react-frontend
npm run dev
```

This runs Vite dev server on `http://localhost:5173` with API proxy to backend.

## Usage

### 1. Upload Documents

- Click the upload zone in the sidebar
- Select one or more PDF files
- Wait for processing (first time downloads embedding models)

### 2. Ask Questions

- Type your question in the chat input
- Press Enter or click Send
- Wait for the AI to process:
  - Hybrid retrieval (semantic + BM25)
  - Reranking with cross-encoder
  - Answer generation with Ollama

### 3. View Sources

- Click "Sources" dropdown to see retrieved chunks
- Each source shows document name, page number, and snippet
- Helps verify answer accuracy

### 4. Manage Documents

- View all uploaded documents in sidebar
- See statistics: pages, chunks, file size
- Delete documents with trash icon

## API Endpoints

### Health Check
```
GET /api/health
```
Returns system status, Ollama availability, document count

### Document Management
```
GET  /api/documents          # List all documents
POST /api/documents/upload   # Upload and index PDF
GET  /api/documents/{id}     # Get document details
DELETE /api/documents/{id}   # Delete document
```

### Chat & Search
```
POST /api/chat    # Ask question, get answer with sources
POST /api/search  # Retrieval only (no LLM generation)
```

## Configuration

Edit `backend/.env` or `backend/app/config.py`:

```python
# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Reranker
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval
SEMANTIC_TOP_K = 10
BM25_TOP_K = 10
HYBRID_WEIGHT_SEMANTIC = 0.6
HYBRID_WEIGHT_BM25 = 0.4
FINAL_TOP_K = 5

# Ollama
DEFAULT_MODEL = "phi3:mini"
OLLAMA_BASE_URL = "http://localhost:11434"
```

## How It Works

### Document Ingestion Pipeline

1. **PDF Upload** → Generate SHA256 hash for deduplication
2. **Text Extraction** → PyPDFLoader extracts text per page
3. **Chunking** → RecursiveCharacterTextSplitter creates 800-char chunks with 150-char overlap
4. **Metadata Enrichment** → Add document_id, filename, page, chunk_id
5. **Embedding** → sentence-transformers generates 384-dim vectors
6. **Vector Storage** → ChromaDB persists embeddings
7. **BM25 Indexing** → Build keyword search index
8. **Metadata Storage** → Save document stats to JSON

### Query Pipeline

1. **User Question** → Preprocess query
2. **Semantic Search** → ChromaDB retrieves top 10 by vector similarity
3. **BM25 Search** → rank-bm25 retrieves top 10 by keyword match
4. **Hybrid Fusion** → Combine with weighted scores (0.6 semantic + 0.4 BM25)
5. **Reranking** → Cross-encoder scores each candidate against query
6. **Top-K Selection** → Select 5 best chunks
7. **Context Formatting** → Format chunks with page citations
8. **LLM Generation** → Ollama generates grounded answer
9. **Response** → Return answer + source citations

## Models Used

| Component | Model | Size | Purpose |
|-----------|-------|------|---------|
| Embeddings | all-MiniLM-L6-v2 | 80MB | Fast semantic search |
| Reranker | ms-marco-MiniLM-L-6-v2 | 90MB | Retrieval refinement |
| LLM | phi3:mini | 2.3GB | Answer generation |

All models run locally on CPU.

## Performance Tips

- **First upload is slow**: Downloads embedding models (~170MB)
- **Subsequent uploads are fast**: Models are cached
- **Chunk count matters**: More chunks = slower retrieval
- **Ollama warmup**: First query takes longer (model loading)

## Troubleshooting

### Ollama Not Available

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull model if missing
ollama pull phi3:mini
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt
```

### Frontend Not Loading

```bash
# Rebuild frontend
cd react-frontend
npm run build

# Check backend logs for errors
```

### ChromaDB Errors

```bash
# Delete and rebuild indexes
rm -rf backend/storage/chroma
rm -rf backend/storage/bm25

# Re-upload documents
```

## Upgrading from v1.0

If you have the old Streamlit prototype:

1. ✅ Your PDFs in `data/` were copied to `backend/data/documents/`
2. ✅ Your old `chroma_db/` was backed up to `chroma_backup/`
3. ❌ You need to re-upload PDFs to build new indexes
4. ❌ Old Streamlit app (`app.py`) is no longer used

## Next Steps

### Phase 6: Evaluation
- [ ] Implement recall@k, precision@k, MRR metrics
- [ ] Answer faithfulness scoring
- [ ] Latency monitoring

### Phase 7: Production
- [ ] Docker containerization
- [ ] PostgreSQL for metadata
- [ ] Authentication & user management
- [ ] Logging & monitoring
- [ ] Cloud deployment

## Tech Stack

- **Backend**: FastAPI, LangChain, ChromaDB, sentence-transformers
- **Frontend**: React, Vite, Lucide Icons, react-markdown
- **LLM**: Ollama (phi3:mini)
- **Vector DB**: ChromaDB
- **Keyword Search**: rank-bm25

## License

MIT

## Credits

Built with modern RAG best practices:
- Hybrid retrieval for better coverage
- Reranking for precision
- Local LLM for privacy
- Source citations for trust

---

**RAGForge v2.0** - Real RAG Architecture for Local Document Q&A
