import React from 'react';
import Layout from '@theme/Layout';
import RAGChatbot from '../components/RAGChatbot';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

function RagChatbotPage() {
  const { siteConfig } = useDocusaurusContext();
  const backendApiUrl =
    (siteConfig.customFields?.backendApiUrl as string) ||
    'http://localhost:8000';

  // Pass backendApiUrl to RAGChatbot component if needed for direct API calls,
  // or modify RAGChatbot to consume it from context if the API client is tightly coupled.
  // For now, let's assume RAGChatbot will use the `queryRag` function
  // which now expects the `backendApiUrl` as an argument.
  // The RAGChatbot component needs to be updated to accept `queryRag` or `backendApiUrl` as a prop
  // or `queryRag` needs to be initialized with `backendApiUrl`.

  return (
    <Layout title="RAG Chatbot" description="Chat with your textbook content.">
      <main className="container margin-vert--lg">
        <h1>RAG Chatbot</h1>
        <p>
          Ask questions about the textbook content and get AI-generated answers.
        </p>
        <RAGChatbot backendApiUrl={backendApiUrl} />
      </main>
    </Layout>
  );
}

export default RagChatbotPage;
