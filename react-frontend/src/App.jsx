import React, { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './Sidebar';
import ChatArea from './ChatArea';
import { fetchHealth, fetchDocuments, uploadDocument, deleteDocument, chatQuery } from './api';

function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [toasts, setToasts] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const toastIdRef = useRef(0);

  useEffect(() => {
    loadInitialData();
  }, []);

  // Auto-remove toasts after 4 seconds
  useEffect(() => {
    if (toasts.length === 0) return;
    const timer = setTimeout(() => {
      setToasts(prev => prev.slice(1));
    }, 4000);
    return () => clearTimeout(timer);
  }, [toasts]);

  const addToast = useCallback((message, type = 'info') => {
    const id = ++toastIdRef.current;
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const loadInitialData = async () => {
    try {
      const [h, docsArray] = await Promise.all([
        fetchHealth(),
        fetchDocuments()
      ]);
      setHealth(h);
      setDocuments(docsArray);
    } catch (e) {
      console.error("Failed to load initial data", e);
    }
  };

  const handleUpload = async (file) => {
    if (isUploading) return;
    
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const res = await uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });
      
      await loadInitialData();

      if (res.status === 'already_exists') {
        addToast(`"${file.name}" is already indexed`, 'info');
      } else {
        const docInfo = res.document;
        addToast(`Indexed "${docInfo.filename}" — ${docInfo.pages} pages, ${docInfo.chunks} chunks`, 'success');
        
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: `✅ Successfully indexed **${docInfo.filename}**\n\n📄 **Pages:** ${docInfo.pages}\n📦 **Chunks:** ${docInfo.chunks}\n\nYou can now ask questions about this document!`
        }]);
      }
    } catch (e) {
      console.error("Upload failed", e);
      addToast(`Upload failed: ${e.message}`, 'error');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await deleteDocument(documentId);
      await loadInitialData();
      addToast('Document deleted successfully', 'success');
    } catch (e) {
      console.error("Delete failed", e);
      addToast(`Delete failed: ${e.message}`, 'error');
    }
  };

  const handleSendMessage = async (text) => {
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsThinking(true);
    
    try {
      const res = await chatQuery(text);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: res.answer,
        sources: res.sources,
        ollamaActive: res.ollama_active
      }]);
    } catch (e) {
      console.error("Query failed", e);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `I encountered an error processing your request: ${e.message}\n\nPlease try again or check that the backend is running.`
      }]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  return (
    <div className="app-container">
      <Sidebar 
        documents={documents} 
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        health={health}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
        uploadProgress={uploadProgress}
        isUploading={isUploading}
      />
      <ChatArea 
        messages={messages}
        onSendMessage={handleSendMessage}
        isThinking={isThinking}
        documentsCount={documents.length}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
      />
      
      {/* Toast notifications */}
      {toasts.length > 0 && (
        <div className="toast-container">
          {toasts.map(toast => (
            <div key={toast.id} className={`toast ${toast.type}`}>
              {toast.type === 'success' && '✓ '}
              {toast.type === 'error' && '✕ '}
              {toast.type === 'info' && 'ℹ '}
              {toast.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
