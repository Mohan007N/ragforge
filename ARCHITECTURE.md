# RAGForge - Complete Architecture & Technology Stack

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 5173/Dev)               │  │
│  │  - Components: App, ChatArea, Sidebar                     │  │
│  │  - API Client (api.js)                                    │  │
│  │  - Vite Build Tool                                        │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          FastAPI Backend (Port 8000)                      │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  REST API Endpoints                                 │  │  │
│  │  │  - POST /api/upload      → Upload PDF              │  │  │
│  │  │  - GET  /api/documents   → List documents          │  │  │
│  │  │  - POST /api/select_document → Switch doc          │  │  │
│  │  │  - POST /api/query       → Ask questions           │  │  │
│  │  │  - GET  /api/health      → System status           │  │  │
│  │  │  - GET  /                → Serve frontend           │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Middleware                                         │  │  │
│  │  │  - CORS (allow all origins)                        │  │  │
│  │  │  - Static file serving (/frontend)                 │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    rag_pipeline.py                        │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  1. Document Processing                          │    │  │
│  │  │     - PyPDFLoader (load PDF)                     │    │  │
│  │  │     - Metadata enrichment (filename, page)       │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                     ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  2. Semantic Chunking (300 chars)               │    │  │
│  │  │     - SemanticChunker (embedding-based)          │    │  │
│  │  │     - Breakpoint detection (95th percentile)     │    │  │
│  │  │     - Post-split to 300 characters               │    │  │
│  │  │     - Preserve metadata across chunks            │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                     ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  3. Embedding Generation                         │    │  │
│  │  │     - HuggingFace Embeddings                     │    │  │
│  │  │     - Model: sentence-transformers/              │    │  │
│  │  │              all-MiniLM-L6-v2                    │    │  │
│  │  │     - Dimension: 384                             │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                     ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  4. Query Processing                             │    │  │
│  │  │     - Semantic search (top-k retrieval)          │    │  │
│  │  │     - Context formatting with page refs          │    │  │
│  │  │     - LLM prompt construction                    │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   STORAGE LAYER          │  │    LLM LAYER             │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │  ChromaDB          │  │  │  │  Ollama            │  │
│  │  Vector Database   │  │  │  │  (Local LLM)       │  │
│  │  - Persist to disk │  │  │  │  - phi3:mini       │  │
│  │  - Cosine similarity│  │  │  │  - Port: 11434    │  │
│  │  - Metadata filter │  │  │  │  - Temp: 0.1       │  │
│  └────────────────────┘  │  │  └────────────────────┘  │
│  ┌────────────────────┐  │  └──────────────────────────┘
│  │  File System       │  │
│  │  - /data/*.pdf     │  │
│  │  - /chroma_db/*    │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

## 🔧 Technology Stack

### **Frontend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 19.2.8 | UI library |
| **Build Tool** | Vite | 8.2.0 | Fast dev server & bundler |
| **Language** | JavaScript | ES6+ | Programming language |
| **Styling** | CSS3 | - | Glassmorphic design |
| **Icons** | Lucide React | 1.28.0 | Icon library |
| **Markdown** | React Markdown | 10.1.0 | Render formatted responses |
| **HTTP Client** | Fetch API | Native | API communication |
| **Linter** | Oxlint | 1.75.0 | Code quality |

### **Backend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | Async web framework |
| **Server** | Uvicorn | Latest | ASGI server |
| **Language** | Python | 3.11.0 | Programming language |
| **Validation** | Pydantic | Latest | Data validation |
| **File Upload** | python-multipart | Latest | Handle multipart forms |
| **HTTP Client** | Requests | Latest | Check Ollama status |

### **RAG & AI Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **RAG Framework** | LangChain | Latest | LLM orchestration |
| **LangChain Core** | langchain-community | Latest | Community integrations |
| **LangChain Ollama** | langchain-ollama | Latest | Ollama integration |
| **LangChain Chroma** | langchain-chroma | Latest | ChromaDB integration |
| **Experimental** | langchain-experimental | Latest | Semantic chunking |
| **PDF Parser** | PyPDF | Latest | Extract text from PDFs |
| **Embeddings** | sentence-transformers | Latest | Text embeddings |
| **Embedding Model** | all-MiniLM-L6-v2 | - | 384-dim embeddings |
| **Vector DB** | ChromaDB | Latest | Vector storage & search |
| **LLM** | Ollama (phi3:mini) | Latest | Local language model |

## 📊 Data Flow

### **Document Upload Flow**
```
1. User uploads PDF via React UI
   ↓
2. POST /api/upload (multipart/form-data)
   ↓
3. Save to /data/{filename}.pdf
   ↓
4. PyPDFLoader extracts text + metadata
   ↓
5. SemanticChunker splits by meaning
   ↓
6. Post-process to 300 char chunks
   ↓
7. Generate embeddings (all-MiniLM-L6-v2)
   ↓
8. Store in ChromaDB with metadata
   ↓
9. Return success + doc stats (pages, chunks)
   ↓
10. Update UI with new document
```

### **Query Flow**
```
1. User types question in chat
   ↓
2. POST /api/query { question, k, temperature, model_name }
   ↓
3. Embed question using same model
   ↓
4. Semantic search in ChromaDB (top-k=4)
   ↓
5. Retrieve relevant chunks with metadata
   ↓
6. Format context with page references
   ↓
7. Check Ollama availability
   ↓
8a. If Ollama online:
    - Send prompt to Ollama (phi3:mini)
    - Get LLM-generated answer
   ↓
8b. If Ollama offline:
    - Return extracted context only
   ↓
9. Return answer + sources to frontend
   ↓
10. Render markdown response in UI
```

## 🗂️ File Structure

```
ragforge/
│
├── main.py                          # FastAPI application entry point
│   ├── App instance
│   ├── CORS middleware
│   ├── API routes (/api/*)
│   ├── Static file serving
│   └── ApplicationState (active doc tracking)
│
├── rag_pipeline.py                  # RAG logic implementation
│   ├── get_embeddings()            # Cached embedding model
│   ├── check_ollama_status()       # Health check
│   ├── process_pdf()               # PDF → Chunks → Vector DB
│   └── query_rag_pipeline()        # Query → Retrieval → LLM
│
├── requirements.txt                 # Python dependencies
│
├── data/                            # PDF storage
│   ├── AD4502 DL Unit II.pdf
│   └── MLOps_Unit2_E.pdf
│
├── chroma_db/                       # Vector database persistence
│   └── {collection_name}/
│       ├── chroma.sqlite3
│       └── {uuid}/
│           ├── data_level0.bin
│           ├── header.bin
│           ├── length.bin
│           └── link_lists.bin
│
├── frontend/                        # Built React app (production)
│   ├── index.html
│   ├── favicon.svg
│   ├── icons.svg
│   └── assets/
│       ├── index-{hash}.js
│       └── index-{hash}.css
│
└── react-frontend/                  # React source (development)
    ├── src/
    │   ├── main.jsx                # React entry point
    │   ├── App.jsx                 # Main component
    │   ├── ChatArea.jsx            # Chat interface
    │   ├── Sidebar.jsx             # Document management
    │   ├── api.js                  # API client
    │   └── index.css               # Global styles
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    ├── index.html                  # HTML template
    ├── package.json                # Node dependencies
    ├── vite.config.js              # Build configuration
    └── .oxlintrc.json              # Linter config
```

## 🔐 Security Features

- **CORS**: Configured for all origins (development mode)
- **File validation**: Only PDF files accepted
- **Error handling**: Comprehensive try-catch blocks
- **Timeout handling**: Request timeouts for external services
- **Input sanitization**: Pydantic models validate all inputs

## ⚡ Performance Optimizations

1. **Cached Embeddings**: Global embedding model instance (avoid reloading)
2. **Semantic Chunking**: Better context preservation
3. **Small Chunks (300 chars)**: Faster embedding & retrieval
4. **Persistent ChromaDB**: No re-indexing on restart
5. **Vite Build**: Optimized production bundle
6. **Async FastAPI**: Non-blocking I/O operations

## 🎯 Key Features

### **1. Semantic Chunking**
- Uses embedding similarity for intelligent splitting
- Preserves contextual meaning
- 95th percentile breakpoint threshold
- Post-split to 300 characters

### **2. Hybrid RAG Architecture**
- Vector similarity search (ChromaDB)
- Embedding-based retrieval (all-MiniLM-L6-v2)
- LLM synthesis (Ollama/phi3:mini)
- Graceful degradation (works without Ollama)

### **3. Modern UI/UX**
- Glassmorphic design
- Real-time chat interface
- Source citation with expandable context
- Responsive layout
- Dark theme optimized

### **4. Document Management**
- Multi-document support
- Active document switching
- Document metadata tracking
- File size & chunk count display

## 🌐 API Endpoints

### **GET /api/health**
**Response:**
```json
{
  "status": "online",
  "ollama": {
    "available": true,
    "models": ["phi3:mini"],
    "message": "Ollama server is active."
  },
  "active_document": {
    "name": "document.pdf",
    "pages": 10,
    "chunks": 150,
    "is_indexed": true
  }
}
```

### **GET /api/documents**
**Response:**
```json
{
  "documents": [
    {
      "name": "document.pdf",
      "size_mb": 2.5,
      "is_active": true
    }
  ]
}
```

### **POST /api/upload**
**Request:** `multipart/form-data` with file
**Response:**
```json
{
  "status": "success",
  "message": "Successfully processed and indexed 'document.pdf'",
  "document": {
    "name": "document.pdf",
    "pages": 10,
    "chunks": 150
  }
}
```

### **POST /api/select_document**
**Request:**
```json
{
  "filename": "document.pdf"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Switched active document to 'document.pdf'",
  "document": {
    "name": "document.pdf",
    "pages": 10,
    "chunks": 150
  }
}
```

### **POST /api/query**
**Request:**
```json
{
  "question": "What is machine learning?",
  "k": 4,
  "temperature": 0.1,
  "model_name": "phi3:mini"
}
```
**Response:**
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "chunk_id": 1,
      "content": "...",
      "page": 5,
      "source": "document.pdf"
    }
  ],
  "ollama_active": true,
  "message": "Success"
}
```

## 📦 Deployment

### **Local Development**
```bash
# Backend
python main.py

# Frontend Dev Server
cd react-frontend
npm run dev

# Build Frontend
npm run build
```

### **Production Considerations**
- Add authentication/authorization
- Configure CORS properly
- Use environment variables
- Add rate limiting
- Set up reverse proxy (nginx)
- Enable HTTPS
- Add logging & monitoring
- Database backups

## 🔄 Model Information

### **Embedding Model**
- **Name**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Max sequence**: 256 tokens
- **Size**: ~90MB
- **Speed**: Fast (CPU-friendly)

### **LLM Model**
- **Name**: phi3:mini
- **Provider**: Ollama
- **Parameters**: ~3.8B
- **Context**: 4K tokens
- **Quantization**: Q4_K_M
- **Size**: ~2.3GB

## 💡 Design Patterns

1. **Singleton Pattern**: Cached embedding model
2. **Factory Pattern**: Document processing pipeline
3. **Strategy Pattern**: Ollama fallback mechanism
4. **Repository Pattern**: ChromaDB abstraction
5. **MVC Architecture**: Separated concerns (React/FastAPI/RAG)

---

**Built with ❤️ using modern web technologies and AI frameworks**
