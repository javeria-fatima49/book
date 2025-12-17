import React, { useState, useEffect } from 'react';
import {
  queryRag,
  RagQueryRequest,
  RagQueryResponse,
} from '../services/rag_api_client';
import './RAGChatbot.css';

/**
 * Props for the RAGChatbot component.
 */
interface RAGChatbotProps {
  /** The base URL for the backend API. */
  backendApiUrl: string;
  /** Optional book title to display */
  bookTitle?: string;
  /** Optional book author to display */
  bookAuthor?: string;
}

/**
 * A React functional component that implements a Retrieval-Augmented Generation (RAG) chatbot
 * specifically designed for book content.
 * It allows users to ask questions about the book, displays AI-generated answers with sources,
 * and maintains a chat history.
 *
 * @param {RAGChatbotProps} { backendApiUrl, bookTitle, bookAuthor } - The props for the component
 */
const RAGChatbot: React.FC<RAGChatbotProps> = ({ backendApiUrl, bookTitle, bookAuthor }) => {
  /** @type {Array<Object>} messages - State to store the chat history, including user and AI messages. */
  const [messages, setMessages] = useState<
    { type: 'user' | 'ai'; text: string; sources?: any[] }[]
  >([]);
  /** @type {string} input - State to store the current value of the user's input field. */
  const [input, setInput] = useState<string>('');
  /** @type {boolean} loading - State to indicate if an AI response is currently being loaded. */
  const [loading, setLoading] = useState<boolean>(false);

  // Add welcome message when component mounts
  useEffect(() => {
    let welcomeText = "Hello! I'm your book assistant. ";

    if (bookTitle && bookAuthor) {
      welcomeText += `This is based on "${bookTitle}" by ${bookAuthor}. `;
    } else if (bookTitle) {
      welcomeText += `This is based on "${bookTitle}". `;
    } else if (bookAuthor) {
      welcomeText += `This is based on a book by ${bookAuthor}. `;
    }

    welcomeText += "Ask me anything about the book content, and I'll find the relevant information for you.";

    const welcomeMessage = {
      type: 'ai' as const,
      text: welcomeText
    };
    setMessages([welcomeMessage]);
  }, [bookTitle, bookAuthor]);

  /**
   * Handles the submission of a user query.
   * Sends the query to the backend, updates the chat history, and manages loading states.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: { type: 'user'; text: string } = { type: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const request: RagQueryRequest = { query: input };
      const data: RagQueryResponse = await queryRag(request, backendApiUrl);

      const aiMessage: { type: 'ai'; text: string; sources: any[] } = {
        type: 'ai',
        text: data.answer,
        sources: data.sources || [],
      };

      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (error) {
      console.error('Error fetching RAG response:', error);
      const errorMessage: { type: 'ai'; text: string } = {
        type: 'ai',
        text: 'Sorry, I encountered an issue processing your question. Please try again.',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-chatbot-container">
      <div className="chat-header">
        <h3>Book Assistant</h3>
        {bookTitle && (
          <div className="book-info">
            <p><strong>Book:</strong> {bookTitle}</p>
            {bookAuthor && <p><strong>Author:</strong> {bookAuthor}</p>}
          </div>
        )}
      </div>
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.type}`}>
            <div className="message-content">
              <p>{msg.text}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="chat-sources">
                  <strong>Reference:</strong>
                  <ul>
                    {msg.sources.map((source, srcIndex) => (
                      <li key={srcIndex}>
                        <span>Page/Section: {source.metadata.chapter_title || source.metadata.section_title || 'N/A'}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="chat-message ai"><div className="typing-indicator">Thinking...</div></div>}
      </div>
      <form className="chat-input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the book content..."
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="send-button">
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default RAGChatbot;
