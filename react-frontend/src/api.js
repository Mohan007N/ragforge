// RAGForge API Client
const API_BASE = '/api';

export const fetchHealth = async () => {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health status');
  return res.json();
};

export const fetchDocuments = async () => {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  const data = await res.json();
  // Transform backend format to match frontend expectations
  return data.documents.map(doc => ({
    document_id: doc.name,
    filename: doc.name,
    pages: 0, // Backend doesn't provide this in list
    chunks: 0, // Backend doesn't provide this in list
    file_size_mb: doc.size_mb,
    is_active: doc.is_active
  }));
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Upload failed');
  }
  return res.json();
};

export const deleteDocument = async (filename) => {
  // Backend doesn't have delete endpoint, we'll need to add it
  throw new Error('Delete functionality not implemented in backend');
};

export const selectDocument = async (filename) => {
  const res = await fetch(`${API_BASE}/select_document`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Select failed');
  }
  return res.json();
};

export const chatQuery = async (question, k = 4, temperature = 0.1, modelName = 'phi3:mini') => {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question, 
      k, 
      temperature, 
      model_name: modelName 
    }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Query failed');
  }
  return res.json();
};
