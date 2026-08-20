// RAGForge API Client
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/api`
  : '/api';

/**
 * Extract error message from a response, handling both JSON and non-JSON errors.
 */
async function extractError(res) {
  try {
    const data = await res.json();
    return data.detail || data.message || data.error || 'An unknown error occurred';
  } catch {
    return `Request failed with status ${res.status}`;
  }
}

export const fetchHealth = async () => {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health status');
  return res.json();
};

export const fetchDocuments = async () => {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  const data = await res.json();
  
  // Support both array response (v2) and object with documents array (v1)
  const docsList = Array.isArray(data) ? data : (data.documents || []);
  return docsList.map(doc => ({
    document_id: doc.document_id || doc.name,
    filename: doc.filename || doc.name,
    pages: doc.pages !== undefined ? doc.pages : 0,
    chunks: doc.chunks !== undefined ? doc.chunks : 0,
    file_size_mb: doc.file_size_mb !== undefined ? doc.file_size_mb : (doc.size_mb || 0),
    is_active: doc.is_active !== undefined ? doc.is_active : true
  }));
};

/**
 * Upload a document with progress tracking.
 * @param {File} file - The file to upload
 * @param {function} onProgress - Progress callback (0-100)
 */
export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Use XMLHttpRequest for progress tracking
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = Math.round((e.loaded / e.total) * 90); // 90% for upload, 10% for processing
        onProgress(progress);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (onProgress) onProgress(100);
      
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          reject(new Error('Invalid response from server'));
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText);
          reject(new Error(errorData.detail || errorData.message || 'Upload failed'));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });
    
    xhr.addEventListener('error', () => {
      reject(new Error('Network error — check that the backend is running'));
    });
    
    xhr.addEventListener('timeout', () => {
      reject(new Error('Upload timed out — the file may be too large'));
    });
    
    // 5 minute timeout for large files
    xhr.timeout = 300000;
    
    // Try v2 endpoint
    xhr.open('POST', `${API_BASE}/documents/upload`);
    xhr.send(formData);
  });
};

export const deleteDocument = async (documentId) => {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const errorMsg = await extractError(res);
    throw new Error(errorMsg);
  }
  return res.json();
};

export const selectDocument = async (filename) => {
  const res = await fetch(`${API_BASE}/select_document`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename }),
  });
  if (!res.ok) {
    const errorMsg = await extractError(res);
    throw new Error(errorMsg);
  }
  return res.json();
};

export const chatQuery = async (question, k = 5, temperature = 0.1, modelName = 'phi3:mini') => {
  // Try v2 endpoint first (/api/chat), fallback to /api/query
  let res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question, 
      top_k: k,
      k, 
      temperature, 
      model_name: modelName 
    }),
  });

  if (!res.ok && res.status === 404) {
    res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        question, 
        k, 
        temperature, 
        model_name: modelName 
      }),
    });
  }

  if (!res.ok) {
    const errorMsg = await extractError(res);
    throw new Error(errorMsg);
  }
  return res.json();
};
