import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, Database, Trash2 } from 'lucide-react';

export default function Sidebar({ documents, onUpload, onDelete, health }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setIsUploading(true);
      await onUpload(file);
      setIsUploading(false);
      e.target.value = null; // reset input
    }
  };

  const handleDelete = async (e, documentId) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this document?')) {
      await onDelete(documentId);
    }
  };

  return (
    <div className="glass-panel sidebar">
      <h2><Database size={24} /> RAGForge v2.0</h2>

      <div className="upload-zone" onClick={handleUploadClick}>
        <UploadCloud size={32} color="var(--text-secondary)" />
        <p>{isUploading ? 'Uploading & Indexing...' : 'Click to Upload PDF'}</p>
        <input 
          type="file" 
          accept=".pdf" 
          ref={fileInputRef} 
          onChange={handleFileChange}
          disabled={isUploading}
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Documents</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          {health?.documents?.total_chunks || 0} chunks
        </span>
      </div>

      <ul className="doc-list">
        {documents.map((doc) => (
          <li 
            key={doc.document_id} 
            className="doc-item"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1 }}>
              <FileText size={16} color="var(--accent-color)" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="doc-item-name" title={doc.filename}>{doc.filename}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                  {doc.pages} pages • {doc.chunks} chunks • {doc.file_size_mb}MB
                </div>
              </div>
            </div>
            <button 
              onClick={(e) => handleDelete(e, doc.document_id)}
              className="delete-btn"
              title="Delete document"
            >
              <Trash2 size={14} />
            </button>
          </li>
        ))}
        {documents.length === 0 && (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', textAlign: 'center', marginTop: '1rem' }}>
            No documents uploaded yet.
          </p>
        )}
      </ul>

      <div className="status-indicator">
        <div className={`dot ${health?.ollama?.available ? 'online' : 'offline'}`}></div>
        <span>Ollama: {health?.ollama?.available ? 'Online' : 'Offline'}</span>
      </div>
      
      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
        Hybrid Retrieval + Reranking
      </div>
    </div>
  );
}
