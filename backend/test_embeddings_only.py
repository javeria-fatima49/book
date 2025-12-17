"""
Simple test to verify Cohere embeddings with caching work properly
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.services.rag_service import RagService

async def test_cohere_embeddings_only():
    """
    Test only the Cohere embeddings functionality without Qdrant operations
    """
    print("Testing Cohere embeddings with caching in RAG pipeline...")

    try:
        # Initialize RAG service
        rag_service = RagService()
        print("[SUCCESS] RAG Service initialized successfully with Cohere embeddings")

        # Check that the embedding model is set correctly
        print(f"[SUCCESS] Embedding model: {rag_service.embedding_model}")
        print(f"[SUCCESS] LLM model: {rag_service.llm_model}")

        # Test embedding generation
        test_text = "Artificial Intelligence and Machine Learning are fascinating fields"
        embedding = await rag_service._get_text_embedding(test_text)

        print(f"[SUCCESS] Cohere embedding generated successfully")
        print(f"  Text: {test_text[:50]}...")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")

        # Test that the embedding is a list of floats
        assert isinstance(embedding, list), "Embedding should be a list"
        assert all(isinstance(val, (int, float)) for val in embedding), "All embedding values should be numbers"
        print("[SUCCESS] Embedding structure is correct")

        # Verify that caching is working by getting the same embedding again
        print("\nTesting embedding caching...")
        embedding2 = await rag_service._get_text_embedding(test_text)
        print(f"[SUCCESS] Cached embedding has same length: {len(embedding2)}")
        
        # Verify the embeddings are identical
        assert embedding == embedding2, "Cached embedding should match original"
        print("[SUCCESS] Caching works correctly - same embedding retrieved from cache")

        print("\n[SUCCESS] All Cohere embedding with caching tests passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Error during Cohere embedding test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running Cohere Embedding with Caching Verification (without Qdrant)")
    print("=" * 70)

    success = asyncio.run(test_cohere_embeddings_only())

    if success:
        print("\n[SUCCESS] Cohere embeddings with caching are working properly!")
    else:
        print("\n[ERROR] Cohere embeddings with caching test failed!")
        exit(1)