import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function SourceDropdown({ sources }) {
  const [isOpen, setIsOpen] = useState(false);
  
  if (!sources || sources.length === 0) return null;

  return (
    <div>
      <button className="sources-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        Sources ({sources.length})
      </button>
      {isOpen && (
        <div className="sources-content">
          {sources.map((src, i) => (
            <div key={i} style={{ marginBottom: '0.5rem' }}>
              <strong>Page {src.page}</strong>: {src.content.substring(0, 150)}...
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ChatArea({ messages, onSendMessage, isThinking, documentsCount }) {
  const [input, setInput] = useState('');
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;
    onSendMessage(input);
    setInput('');
  };

  return (
    <div className="glass-panel chat-container">
      <div className="chat-header">
        <div>
          <h1>RAGForge AI Assistant</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
            {documentsCount > 0 ? `Searching across ${documentsCount} document${documentsCount > 1 ? 's' : ''}` : 'Upload documents to begin'}
          </p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            <div className="msg-avatar">
              {msg.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="msg-bubble">
              {msg.sender === 'bot' ? (
                <>
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                  {msg.sources && <SourceDropdown sources={msg.sources} />}
                </>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}
        {isThinking && (
          <div className="message bot">
            <div className="msg-avatar"><Bot size={20} /></div>
            <div className="msg-bubble" style={{ display: 'flex', alignItems: 'center', minHeight: '44px' }}>
              <div className="typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        {documentsCount === 0 && messages.length === 1 && (
          <div style={{ textAlign: 'center', margin: 'auto', color: 'var(--text-secondary)' }}>
            <AlertCircle size={48} style={{ opacity: 0.5, margin: '0 auto 1rem' }} />
            <p>Upload PDF documents to start asking questions.</p>
            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>RAGForge uses semantic search with LLM-powered answers.</p>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="input-wrapper">
          <input 
            type="text" 
            placeholder={documentsCount > 0 ? "Ask a question..." : "Upload documents first..."} 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isThinking}
          />
          <button type="submit" className="send-btn" disabled={isThinking || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
