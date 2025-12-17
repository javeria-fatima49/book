from src.services.rag_service import RagService
import os

# Set up minimal environment variables for testing
os.environ["GEMINI_API_KEY"] = "dummy"
os.environ["COHERE_API_KEY"] = "dummy"

try:
    rag_service = RagService()
    print("+ RAG service initialized successfully with Cohere embeddings!")
    print(f"Embedding model: {rag_service.embedding_model}")
    print(f"LLM model: {rag_service.llm_model}")
except ValueError as e:
    print(f"- RAG service initialization failed: {e}")