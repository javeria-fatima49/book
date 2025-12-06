import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RAGChatbot from '../../src/components/RAGChatbot';
import * as ragApiClient from '../../src/services/rag_api_client';

// Mock the rag_api_client module
jest.mock('../../src/services/rag_api_client', () => ({
  ...jest.requireActual('../../src/services/rag_api_client'),
  queryRag: jest.fn(),
}));

const mockQueryRag = ragApiClient.queryRag as jest.Mock;

describe('RAGChatbot', () => {
  const backendApiUrl = 'http://localhost:8000';

  beforeEach(() => {
    // Reset mocks before each test
    mockQueryRag.mockReset();
  });

  test('renders chat input and send button', () => {
    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    expect(screen.getByPlaceholderText('Ask a question about the textbook...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('displays user message after submission', async () => {
    mockQueryRag.mockResolvedValueOnce({ answer: 'AI response', sources: [] });

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'User question' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('User question')).toBeInTheDocument();
    });
  });

  test('displays AI response after successful submission', async () => {
    const mockAnswer = 'This is an AI generated answer.';
    const mockSources = [
      { text: 'Source 1 text', metadata: { url: 'http://example.com/source1' } },
      { text: 'Source 2 text', metadata: { url: 'http://example.com/source2' } },
    ];
    mockQueryRag.mockResolvedValueOnce({ answer: mockAnswer, sources: mockSources });

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'What is RAG?' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(mockAnswer)).toBeInTheDocument();
      expect(screen.getByText('Sources:')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /http:\/\/example.com\/source1/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /http:\/\/example.com\/source2/i })).toBeInTheDocument();
    });

    expect(mockQueryRag).toHaveBeenCalledWith(
      { query: 'What is RAG?' },
      backendApiUrl
    );
  });

  test('displays loading indicator during API call', async () => {
    // Make the promise never resolve to simulate a long-running API call
    mockQueryRag.mockReturnValueOnce(new Promise(() => {}));

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Tell me about AI.' } });
    fireEvent.click(sendButton);

    expect(screen.getByText('Thinking...')).toBeInTheDocument();
    await waitFor(() => expect(sendButton).toBeDisabled());
    await waitFor(() => expect(input).toBeDisabled());
  });

  test('displays error message on API call failure', async () => {
    mockQueryRag.mockRejectedValueOnce(new Error('Network error'));

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Invalid query' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Sorry, something went wrong. Please try again.')).toBeInTheDocument();
    });
    expect(mockQueryRag).toHaveBeenCalledTimes(1);
  });

  test('clears input field after submission', async () => {
    mockQueryRag.mockResolvedValueOnce({ answer: 'AI response', sources: [] });

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Clear me' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  test('handles Enter key press for submission', async () => {
    mockQueryRag.mockResolvedValueOnce({ answer: 'AI response', sources: [] });

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');

    fireEvent.change(input, { target: { value: 'Enter key test' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 13, charCode: 13 });

    await waitFor(() => {
      expect(screen.getByText('Enter key test')).toBeInTheDocument();
      expect(mockQueryRag).toHaveBeenCalledTimes(1);
    });
  });

  test('displays multiple messages in chat history', async () => {
    mockQueryRag
      .mockResolvedValueOnce({ answer: 'AI response 1', sources: [] })
      .mockResolvedValueOnce({ answer: 'AI response 2', sources: [] });

    render(<RAGChatbot backendApiUrl={backendApiUrl} />);

    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    // First exchange
    fireEvent.change(input, { target: { value: 'User question 1' } });
    fireEvent.click(sendButton);
    await waitFor(() => {
      expect(screen.getByText('User question 1')).toBeInTheDocument();
      expect(screen.getByText('AI response 1')).toBeInTheDocument();
    });

    // Second exchange
    fireEvent.change(input, { target: { value: 'User question 2' } });
    fireEvent.click(sendButton);
    await waitFor(() => {
      expect(screen.getByText('User question 2')).toBeInTheDocument();
      expect(screen.getByText('AI response 2')).toBeInTheDocument();
    });

    // Ensure all messages are present
    const messages = screen.getAllByText(/User question|AI response/);
    expect(messages).toHaveLength(4); // 2 user, 2 AI
    expect(messages[0]).toHaveTextContent('User question 1');
    expect(messages[1]).toHaveTextContent('AI response 1');
    expect(messages[2]).toHaveTextContent('User question 2');
    expect(messages[3]).toHaveTextContent('AI response 2');
  });
});
