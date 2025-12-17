import React, { useState, useEffect } from 'react';
import RAGChatbot from './RAGChatbot';
import './FloatingChatbot.css';

interface FloatingChatbotProps {
  backendApiUrl: string;
  bookTitle?: string;
  bookAuthor?: string;
}

const FloatingChatbot: React.FC<FloatingChatbotProps> = ({
  backendApiUrl,
  bookTitle = 'AI Book',
  bookAuthor = 'Author'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);

  // Show initial greeting to first-time visitors
  useEffect(() => {
    const hasVisited = localStorage.getItem('hasVisitedChatbot');
    if (!hasVisited) {
      setHasInteracted(true);
      localStorage.setItem('hasVisitedChatbot', 'true');
    }
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setHasInteracted(true);
    }
  };

  return (
    <div className="floating-chatbot">
      {isOpen ? (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h4>AI Book Assistant</h4>
            <button
              className="close-button"
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <RAGChatbot
            backendApiUrl={backendApiUrl}
            bookTitle={bookTitle}
            bookAuthor={bookAuthor}
          />
        </div>
      ) : null}

      <button
        className={`chatbot-toggle ${isOpen ? 'open' : ''}`}
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? (
          <span className="close-icon">×</span>
        ) : (
          <div className="chatbot-toggle-content">
            <span className="chat-icon">💬</span>
            <span className="chat-label">Chat</span>
          </div>
        )}
        {!hasInteracted && !isOpen && (
          <span className="notification-dot"></span>
        )}
      </button>
    </div>
  );
};

export default FloatingChatbot;