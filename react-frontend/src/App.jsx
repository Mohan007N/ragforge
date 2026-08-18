import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatArea from './ChatArea';
import { fetchHealth, fetchDocuments, uploadDocument, deleteDocument, chatQuery } from './api';

function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([{ 
    sender: 'bot', 
    text: 'Hello! I am RAGForge v2.0 with hybrid retrieval and reranking. Upload documents and ask me anything!' 
  }]);
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
      
      const docsArray = await fetchDocuments();
      setDocuments(docsArray);
    } catch (e) {
      console.error("Failed to load initial data", e);
    }
  };

  const handleUpload = async (file) => {
    try {
      const res = await uploadDocument(file);
      await loadInitialData();
      
      const docInfo = res.document;
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `✅ Successfully indexed **${docInfo.name}**\n\n📄 Pages: ${docInfo.pages}\n📦 Chunks: ${docInfo.chunks}\n\nYou can now ask questions about this document!` 
      }]);
    } catch (e) {
      console.error("Upload failed", e);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `❌ Upload failed: ${e.message}` 
      }]);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await deleteDocument(documentId);
      await loadInitialData();
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `🗑️ Document deleted successfully.` 
      }]);
    } catch (e) {
      console.error("Delete failed", e);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `❌ Delete failed: ${e.message}` 
      }]);
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
        text: `❌ Sorry, query failed: ${e.message}` 
      }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        documents={documents} 
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        health={health}
      />
      <ChatArea 
        messages={messages}
        onSendMessage={handleSendMessage}
        isThinking={isThinking}
        documentsCount={documents.length}
      />
    </div>
  );
}

export default App;
