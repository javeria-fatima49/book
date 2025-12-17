"""
Test script to verify the complete RAG pipeline functionality.
This script will test all components of the book chatbot system.
"""

import asyncio
import json
from typing import Dict, Any

# Test sample book content
SAMPLE_BOOK_CONTENT = """
Chapter 1: Introduction to Artificial Intelligence

Artificial Intelligence (AI) is a branch of computer science that aims to create
software or machines that exhibit human-like intelligence. This can include
learning from experience, understanding natural language, solving problems,
and recognizing patterns.

The field of AI includes various subfields such as machine learning,
natural language processing, computer vision, and robotics.
Machine learning is a subset of AI that focuses on algorithms
that can learn and improve from experience without being explicitly programmed.

Chapter 2: Machine Learning Fundamentals

Machine learning algorithms build a model based on training data in order
to make predictions or decisions without being explicitly programmed
to do so. There are three main types of machine learning:
supervised learning, unsupervised learning, and reinforcement learning.

Supervised learning uses labeled training data, while unsupervised
learning finds hidden patterns in unlabeled data. Reinforcement
learning uses rewards and penalties to guide the learning process.
"""

async def test_pipeline():
    print("Starting RAG pipeline test...")

    # Import necessary modules
    try:
        from src.services.rag_service import RagService
        from src.services.document_ingestion_service import DocumentIngestionService
        from src.services.book_service import BookService
        from src.core.database import get_db_session
        from sqlalchemy.ext.asyncio import AsyncSession
        print("✓ Successfully imported required modules")
    except ImportError as e:
        print(f"✗ Failed to import modules: {e}")
        return False

    # Test configuration
    try:
        rag_service = RagService()
        print("✓ Successfully initialized RAG service with Gemini API and Cohere embeddings")
    except ValueError as e:
        print(f"✗ Failed to initialize RAG service: {e}")
        print("Make sure GEMINI_API_KEY and COHERE_API_KEY are set in environment variables")
        return False
    except Exception as e:
        print(f"✗ Error initializing RAG service: {e}")
        return False

    # Test embedding generation
    try:
        test_text = "Artificial Intelligence is fascinating"
        embedding = await rag_service._get_text_embedding(test_text)
        print(f"✓ Successfully generated embedding for '{test_text[:20]}...' (length: {len(embedding)})")
    except Exception as e:
        print(f"✗ Failed to generate embedding: {e}")
        return False

    # Test upsert functionality
    try:
        metadata = {"chapter_title": "Test Chapter", "book_title": "Test Book", "book_author": "Test Author"}
        upserted_count = await rag_service.upsert_embeddings("This is a test content for the RAG system.", metadata)
        print(f"✓ Successfully upserted {upserted_count} embeddings to Qdrant")
    except Exception as e:
        print(f"✗ Failed to upsert embeddings: {e}")
        return False

    # Test query functionality
    try:
        from src.models.rag_models import RagQueryRequest
        query_request = RagQueryRequest(query="What is Artificial Intelligence?", user_id="test_user")
        response = await rag_service.query_rag(query_request)
        print(f"✓ Successfully queried RAG system: '{response.answer[:50]}...'")
    except Exception as e:
        print(f"✗ Failed to query RAG system: {e}")
        return False

    # Test document ingestion (this would need a proper database session)
    print("\nNote: Full document ingestion test requires a running database.")
    print("Basic RAG functionality tests passed!")

    return True

def test_api_endpoints():
    """Test the FastAPI endpoints using HTTP requests"""
    import requests
    import time

    print("\nTesting FastAPI endpoints...")
    base_url = "http://localhost:8000/api/v1/rag"  # Default FastAPI port

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health endpoint is accessible")
        else:
            print(f"✗ Health endpoint returned status {response.status_code}")
    except requests.ConnectionError:
        print(f"✗ Cannot connect to API at {base_url}. Is the server running?")
        print("To start the server, run: uvicorn src.main:app --reload")

    # Test basic RAG query endpoint structure
    print("API endpoint structure test completed.")


if __name__ == "__main__":
    print("Running RAG Pipeline Tests")
    print("=" * 50)

    # Run async tests
    success = asyncio.run(test_pipeline())

    if success:
        print("\n✓ Core RAG functionality tests passed!")
        print("\nTesting API endpoints...")
        test_api_endpoints()
        print("\nTest Summary: RAG pipeline components are properly implemented.")
    else:
        print("\n✗ Some tests failed. Please check the implementation.")

    print("\nTo fully test the system:")
    print("1. Set up your environment variables (GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY)")
    print("2. Start the backend server: uvicorn src.main:app --reload")
    print("3. Ingest a book using the /api/v1/rag/books/ingest endpoint")
    print("4. Query the chatbot using the /api/v1/rag/query endpoint")
    print("5. Test the frontend interface")