# RAGForge API Documentation

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

Authentication is optional and disabled by default in development mode.

### Enable Authentication

Set environment variable:
```bash
ENABLE_AUTH=true
API_KEYS=your-secret-key-here
```

### Using API Keys

Include in Authorization header:
```bash
Authorization: Bearer your-secret-key-here
```

## Rate Limiting

**Default**: 60 requests per minute per IP address

Response when exceeded:
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/docs
- **ReDoc**: http://127.0.0.1:8000/api/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/api/openapi.json

---

## Endpoints

### Health & Monitoring

#### GET /api/health

Get system health status

**Response 200**
```json
{
  "status": "online",
  "ollama": {
    "available": true,
    "models": ["phi3:mini"],
    "message": "Ollama server is active."
  },
  "documents": {
    "count": 5,
    "total_chunks": 250
  }
}
```

#### GET /api/metrics

Get application metrics (requires authentication)

**Headers**
```
Authorization: Bearer your-api-key
```

**Response 200**
```json
{
  "application": {
    "uptime_seconds": 3600,
    "total_requests": 150,
    "requests_by_endpoint": {
      "/api/chat": 45,
      "/api/documents": 10
    },
    "average_latency_ms": {
      "/api/chat": 2500,
      "/api/documents": 150
    },
    "total_errors": 2,
    "errors_by_endpoint": {}
  },
  "system": {
    "cpu_percent": 15.2,
    "memory": {
      "total_gb": 16.0,
      "available_gb": 8.5,
      "used_percent": 46.9
    },
    "disk": {
      "total_gb": 500.0,
      "free_gb": 250.0,
      "used_percent": 50.0
    }
  },
  "storage": {
    "documents_size_mb": 125.5,
    "chromadb_size_mb": 45.2,
    "bm25_size_mb": 12.3
  }
}
```

#### GET /api/ready

Kubernetes-style readiness probe

**Response 200**
```json
{
  "ready": true,
  "checks": {
    "embeddings": true,
    "vectorstore": true
  }
}
```

#### GET /api/live

Kubernetes-style liveness probe

**Response 200**
```json
{
  "status": "alive"
}
```

---

### Document Management

#### GET /api/documents

List all uploaded documents

**Response 200**
```json
{
  "documents": [
    {
      "document_id": "abc123def456...",
      "filename": "machine_learning.pdf",
      "pages": 25,
      "chunks": 125,
      "file_size_mb": 2.5,
      "upload_date": "2026-08-12T10:30:00Z"
    }
  ]
}
```

#### POST /api/documents/upload

Upload and index a new PDF document

**Request**
```
Content-Type: multipart/form-data

file: <PDF file>
```

**Response 200**
```json
{
  "status": "success",
  "message": "Successfully processed and indexed 'machine_learning.pdf'",
  "document": {
    "document_id": "abc123def456...",
    "filename": "machine_learning.pdf",
    "pages": 25,
    "chunks": 125,
    "file_size_mb": 2.5,
    "upload_date": "2026-08-12T10:30:00Z"
  }
}
```

**Response 409** (Document already exists)
```json
{
  "status": "already_exists",
  "message": "Document already indexed",
  "document": {
    "document_id": "abc123def456...",
    "filename": "machine_learning.pdf",
    "pages": 25,
    "chunks": 125
  }
}
```

**Response 400** (Invalid file)
```json
{
  "detail": "Only PDF files are supported"
}
```

**Response 413** (File too large)
```json
{
  "detail": "File too large. Maximum size: 50MB"
}
```

#### GET /api/documents/{document_id}

Get details of a specific document

**Response 200**
```json
{
  "document_id": "abc123def456...",
  "filename": "machine_learning.pdf",
  "pages": 25,
  "chunks": 125,
  "file_size_mb": 2.5,
  "upload_date": "2026-08-12T10:30:00Z"
}
```

**Response 404**
```json
{
  "detail": "Document not found"
}
```

#### DELETE /api/documents/{document_id}

Delete a document and remove from all indexes

**Response 200**
```json
{
  "status": "success",
  "message": "Document deleted successfully",
  "document_id": "abc123def456...",
  "chunks_deleted_chroma": 125,
  "chunks_deleted_bm25": 125
}
```

**Response 404**
```json
{
  "detail": "Document not found"
}
```

---

### Chat & Search

#### POST /api/chat

Ask a question and get an AI-generated answer with sources

**Request Body**
```json
{
  "question": "What is machine learning?",
  "top_k": 5,
  "model_name": "phi3:mini",
  "temperature": 0.1
}
```

**Parameters**
- `question` (required): User question (1-5000 characters)
- `top_k` (optional): Number of chunks to retrieve (1-20, default: 5)
- `model_name` (optional): LLM model name (default: "phi3:mini")
- `temperature` (optional): LLM temperature (0-2, default: 0.1)

**Response 200**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It involves training algorithms on datasets to identify patterns and make predictions or decisions. Common types include supervised learning, unsupervised learning, and reinforcement learning.",
  "sources": [
    {
      "chunk_id": 1,
      "content": "Machine learning is a method of data analysis that automates analytical model building...",
      "page": 5,
      "source": "machine_learning.pdf",
      "score": 0.92
    },
    {
      "chunk_id": 2,
      "content": "Types of machine learning include supervised, unsupervised, and reinforcement learning...",
      "page": 7,
      "source": "machine_learning.pdf",
      "score": 0.87
    }
  ],
  "ollama_active": true,
  "message": "Success"
}
```

**Response 400** (No documents)
```json
{
  "answer": "No relevant documents found. Please upload documents first.",
  "sources": [],
  "ollama_active": false,
  "message": "No documents in database"
}
```

**Response 500** (Ollama offline)
```json
{
  "answer": "**Note: Local Ollama service is currently offline...**\n\n### Retrieved Context Summary...",
  "sources": [...],
  "ollama_active": false,
  "message": "Ollama service offline. Displaying extracted semantic context."
}
```

#### POST /api/search

Retrieve relevant chunks without LLM generation (faster)

**Request Body**
```json
{
  "question": "What is machine learning?",
  "top_k": 5
}
```

**Response 200**
```json
{
  "results": [
    {
      "chunk_id": 1,
      "content": "Machine learning is a method of data analysis...",
      "page": 5,
      "source": "machine_learning.pdf",
      "score": 0.92
    }
  ],
  "count": 5
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Invalid API key"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File too large. Maximum size: 50MB"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "your-api-key"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/documents/upload",
        files={"file": f},
        headers=headers
    )
    print(response.json())

# Ask question
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"question": "What is machine learning?"},
    headers=headers
)
print(response.json()["answer"])
```

### cURL

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Upload document
curl -X POST \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf" \
  http://127.0.0.1:8000/api/documents/upload

# Ask question
curl -X POST \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}' \
  http://127.0.0.1:8000/api/chat

# List documents
curl -H "Authorization: Bearer your-api-key" \
  http://127.0.0.1:8000/api/documents

# Delete document
curl -X DELETE \
  -H "Authorization: Bearer your-api-key" \
  http://127.0.0.1:8000/api/documents/abc123def456
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://127.0.0.1:8000";
const API_KEY = "your-api-key";

// Upload document
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const uploadResponse = await fetch(`${BASE_URL}/api/documents/upload`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${API_KEY}`
  },
  body: formData
});

const uploadData = await uploadResponse.json();
console.log(uploadData);

// Ask question
const chatResponse = await fetch(`${BASE_URL}/api/chat`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${API_KEY}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    question: "What is machine learning?"
  })
});

const chatData = await chatResponse.json();
console.log(chatData.answer);
```

---

## Webhooks (Future)

Not yet implemented. Planned features:
- Document processing completion
- Query result notifications
- Error alerts

---

## Versioning

Current version: **v2.0.0**

API versioning will be introduced in future releases via URL path:
- `/api/v2/documents`
- `/api/v3/documents`

---

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Security**: See SECURITY.md

---

**Last Updated**: 2026-08-12  
**API Version**: 2.0.0
