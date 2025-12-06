import React, { useState } from 'react';
import {
  queryRag,
  RagQueryRequest,
  RagQueryResponse,
} from '../services/rag_api_client';

/**
 * Props for the RAGChatbot component.
 */
interface RAGChatbotProps {
  /** The base URL for the backend API. */
  backendApiUrl: string;
}

/**
 * A React functional component that implements a Retrieval-Augmented Generation (RAG) chatbot.
 * It allows users to ask questions, displays AI-generated answers with sources,
 * and maintains a chat history.
 *
 * @param {RAGChatbotProps} { backendApiUrl } - The props for the component, including the backend API URL.
 */
const RAGChatbot: React.FC<RAGChatbotProps> = ({ backendApiUrl }) => {
  /** @type {Array<Object>} messages - State to store the chat history, including user and AI messages. */
  const [messages, setMessages] = useState<
    { type: 'user' | 'ai'; text: string; sources?: string[] }[]
  >([]);
  /** @type {string} input - State to store the current value of the user's input field. */
  const [input, setInput] = useState<string>('');
  /** @type {boolean} loading - State to indicate if an AI response is currently being loaded. */
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * Handles the submission of a user query.
   * Sends the query to the backend, updates the chat history, and manages loading states.
   */
  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage: { type: 'user'; text: string } = { type: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const request: RagQueryRequest = { query: input };
      const data: RagQueryResponse = await queryRag(request, backendApiUrl);
      const aiMessage: { type: 'ai'; text: string; sources: string[] } = {
        type: 'ai',
        text: data.answer,
        sources: data.sources.map((s) => s.metadata.url as string),
      };

      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (error) {
      console.error('Error fetching RAG response:', error);
      const errorMessage: { type: 'ai'; text: string } = {
        type: 'ai',
        text: 'Sorry, something went wrong. Please try again.',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-chatbot-container">
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.type}`}>
            <p>{msg.text}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="chat-sources">
                <strong>Sources:</strong>
                <ul>
                  {msg.sources.map((source, srcIndex) => (
                    <li key={srcIndex}>
                      <a
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {source}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="chat-message ai">Thinking...</div>}
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSubmit();
            }
          }}
          placeholder="Ask a question about the textbook..."
          disabled={loading}
        />
        <button onClick={handleSubmit} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default RAGChatbot;
