import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, User, Sparkles, ChevronDown, ChevronRight, PanelLeftOpen, RotateCcw, Zap, FileSearch, BookOpen, HelpCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

/* ─── Source Citation Dropdown ─── */
function SourceDropdown({ sources }) {
  const [isOpen, setIsOpen] = useState(false);
  
  if (!sources || sources.length === 0) return null;

  return (
    <div>
      <button className="sources-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        {sources.length} source{sources.length > 1 ? 's' : ''} cited
      </button>
      {isOpen && (
        <div className="sources-content">
          {sources.map((src, i) => (
            <div key={i} className="source-item">
              <div className="source-item-header">
                {src.source} • Page {src.page}
              </div>
              <div>{src.content.substring(0, 200)}...</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Welcome Screen (shown when no messages) ─── */
function WelcomeScreen({ onPromptClick, documentsCount }) {
  const suggestedPrompts = [
    {
      title: "Summarize document",
      text: "Give me a comprehensive summary of the uploaded document",
      icon: <BookOpen size={16} />
    },
    {
      title: "Find specific info",
      text: "What are the key findings or conclusions mentioned?",
      icon: <FileSearch size={16} />
    },
    {
      title: "Extract insights",
      text: "What are the most important data points or statistics?",
      icon: <Zap size={16} />
    },
    {
      title: "Ask a question",
      text: "Explain the methodology or approach described",
      icon: <HelpCircle size={16} />
    }
  ];

  return (
    <div className="welcome-screen">
      <div className="welcome-logo">
        <Sparkles size={28} />
      </div>
      <h1 className="welcome-title">RAGForge AI</h1>
      <p className="welcome-subtitle">
        {documentsCount > 0
          ? `You have ${documentsCount} document${documentsCount > 1 ? 's' : ''} indexed. Ask anything about your documents — I use hybrid retrieval and reranking to find the best answers.`
          : 'Upload PDF documents and ask intelligent questions. Powered by hybrid retrieval, cross-encoder reranking, and local LLM generation.'
        }
      </p>
      {documentsCount > 0 && (
        <div className="suggested-prompts">
          {suggestedPrompts.map((prompt, idx) => (
            <button
              key={idx}
              className="prompt-card"
              onClick={() => onPromptClick(prompt.text)}
            >
              <div className="prompt-card-title">
                {prompt.title}
              </div>
              {prompt.text}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Main Chat Area ─── */
export default function ChatArea({ messages, onSendMessage, isThinking, documentsCount, sidebarOpen, onToggleSidebar, onNewChat }) {
  const [input, setInput] = useState('');
  const endOfMessagesRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || isThinking) return;
    onSendMessage(input.trim());
    setInput('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePromptClick = (text) => {
    onSendMessage(text);
  };

  const showWelcome = messages.length === 0;

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {!sidebarOpen && (
              <button className="header-action-btn" onClick={onToggleSidebar} title="Open sidebar">
                <PanelLeftOpen size={18} />
              </button>
            )}
            <div>
              <div className="chat-header-title">RAGForge AI</div>
              <div className="chat-header-sub">
                {documentsCount > 0 
                  ? `Searching ${documentsCount} document${documentsCount > 1 ? 's' : ''}`
                  : 'No documents uploaded'}
              </div>
            </div>
          </div>
        </div>
        <div className="chat-header-actions">
          {messages.length > 0 && (
            <button className="header-action-btn" onClick={onNewChat} title="New conversation">
              <RotateCcw size={15} />
              <span>New chat</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages or Welcome */}
      {showWelcome ? (
        <WelcomeScreen 
          onPromptClick={handlePromptClick}
          documentsCount={documentsCount}
        />
      ) : (
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.sender}`}>
              <div className="msg-avatar">
                {msg.sender === 'user' 
                  ? <User size={16} /> 
                  : <Sparkles size={16} />
                }
              </div>
              <div className={`msg-content ${msg.sender === 'user' ? 'user-content' : ''}`}>
                {msg.sender === 'bot' ? (
                  <>
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                    {msg.sources && <SourceDropdown sources={msg.sources} />}
                    {msg.ollamaActive !== undefined && (
                      <div className={`ollama-badge ${msg.ollamaActive ? 'active' : 'inactive'}`}>
                        <Zap size={10} />
                        {msg.ollamaActive ? 'Ollama LLM' : 'Context mode'}
                      </div>
                    )}
                  </>
                ) : (
                  msg.text
                )}
              </div>
            </div>
          ))}
          
          {/* Thinking indicator */}
          {isThinking && (
            <div className="message-row bot">
              <div className="msg-avatar">
                <Sparkles size={16} />
              </div>
              <div className="msg-content">
                <div className="thinking-indicator">
                  <div className="thinking-dot" />
                  <div className="thinking-dot" />
                  <div className="thinking-dot" />
                </div>
              </div>
            </div>
          )}
          
          <div ref={endOfMessagesRef} />
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="input-container">
          <textarea
            ref={textareaRef}
            placeholder={documentsCount > 0 ? "Ask a question about your documents..." : "Upload a document first to start asking questions..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isThinking}
            rows={1}
          />
          <button 
            type="submit" 
            className="send-btn" 
            disabled={isThinking || !input.trim()}
            title="Send message"
          >
            <Send size={16} />
          </button>
        </form>
        <div className="input-hint">
          Press Enter to send · Shift + Enter for new line
        </div>
      </div>
    </div>
  );
}
