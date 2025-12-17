/*
 * Example JavaScript code for frontend to query the RAG backend
 * This should be integrated into your Docusaurus frontend
 */

class RAGChatbot {
  constructor(backendUrl = 'http://localhost:8000') {
    this.backendUrl = backendUrl;
  }

  async query(message, userId = null) {
    try {
      const response = await fetch(`${this.backendUrl}/api/v1/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          user_id: userId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error querying RAG backend:', error);
      throw error;
    }
  }
}

// Usage example:
async function example() {
  const chatbot = new RAGChatbot(); // Uses default backend URL (http://localhost:8000)
  
  try {
    const result = await chatbot.query("Explain module 1", "user123");
    console.log("Answer:", result.answer);
    console.log("Sources:", result.sources);
  } catch (error) {
    console.error("Failed to get response:", error);
  }
}

// Example of how to integrate with your Docusaurus site
function setupChatbot() {
  // Find your chat input element
  const chatInput = document.getElementById('chat-input');
  const chatButton = document.getElementById('chat-button');
  const chatOutput = document.getElementById('chat-output');

  if (!chatInput || !chatButton) {
    console.log('Chat elements not found, skipping chatbot setup');
    return;
  }

  const chatbot = new RAGChatbot();

  chatButton.addEventListener('click', async () => {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // Add user message to chat
    addToChat('user', userMessage);
    chatInput.value = '';

    try {
      const response = await chatbot.query(userMessage);
      addToChat('bot', response.answer);
    } catch (error) {
      addToChat('bot', 'Sorry, I encountered an error processing your request.');
      console.error('Chat error:', error);
    }
  });

  function addToChat(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    messageElement.textContent = message;
    chatOutput.appendChild(messageElement);
    chatOutput.scrollTop = chatOutput.scrollHeight;
  }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', setupChatbot);