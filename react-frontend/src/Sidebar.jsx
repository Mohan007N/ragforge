import React, { useRef, useState, useCallback } from 'react';
import { UploadCloud, FileText, Trash2, Plus, PanelLeftClose, Sparkles } from 'lucide-react';

export default function Sidebar({ 
  documents, 
  onUpload, 
  onDelete, 
  health, 
  isOpen, 
  onToggle, 
  onNewChat,
  uploadProgress,
  isUploading
}) {
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleUploadClick = () => {
    if (!isUploading) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await onUpload(file);
      e.target.value = null;
    }
  };

  const handleDelete = async (e, documentId) => {
    e.stopPropagation();
    if (confirm('Delete this document and all its indexed data?')) {
      await onDelete(documentId);
    }
  };

  // Drag & drop handlers
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(f => f.name.toLowerCase().endsWith('.pdf'));
    
    if (pdfFile) {
      await onUpload(pdfFile);
    }
  }, [onUpload]);

  const totalChunks = health?.documents?.total_chunks || 0;
  const ollamaOnline = health?.ollama?.available;

  return (
    <div className={`sidebar ${isOpen ? '' : 'collapsed'}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Sparkles size={18} />
          </div>
          <span>RAGForge</span>
        </div>
        <button 
          className="sidebar-toggle-btn" 
          onClick={onToggle}
          title="Close sidebar"
        >
          <PanelLeftClose size={18} />
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        <Plus size={16} />
        New conversation
      </button>

      {/* Upload Zone */}
      <div 
        className={`upload-zone ${dragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
        onClick={handleUploadClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon">
          <UploadCloud size={24} />
        </div>
        <span className="upload-label">
          {isUploading ? 'Processing document...' : 'Upload PDF'}
        </span>
        <span className="upload-sublabel">
          {isUploading ? '' : 'Click or drag & drop'}
        </span>
        <input 
          type="file" 
          accept=".pdf" 
          ref={fileInputRef} 
          onChange={handleFileChange}
          disabled={isUploading}
        />
        {isUploading && (
          <div 
            className="upload-progress" 
            style={{ width: `${Math.max(uploadProgress, 15)}%` }} 
          />
        )}
      </div>

      {/* Documents Section */}
      <div className="docs-section-header">
        <span className="docs-section-title">Documents</span>
        <span className="docs-section-count">
          {totalChunks > 0 ? `${totalChunks} chunks` : ''}
        </span>
      </div>

      <ul className="doc-list">
        {documents.map((doc, index) => (
          <li 
            key={doc.document_id} 
            className="doc-item"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="doc-item-info">
              <div className="doc-item-icon">
                <FileText size={16} />
              </div>
              <div className="doc-item-details">
                <div className="doc-item-name" title={doc.filename}>
                  {doc.filename}
                </div>
                <div className="doc-item-meta">
                  {doc.pages} pages · {doc.chunks} chunks · {doc.file_size_mb} MB
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
          <p className="empty-docs-msg">
            No documents uploaded yet.
            <br />
            Upload a PDF to get started.
          </p>
        )}
      </ul>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="status-row">
          <div className={`status-dot ${ollamaOnline ? 'online' : 'offline'}`} />
          <span>Ollama: {ollamaOnline ? 'Connected' : 'Offline'}</span>
        </div>
        <div className="sidebar-footnote">
          Hybrid retrieval · Cross-encoder reranking
        </div>
      </div>
    </div>
  );
}
