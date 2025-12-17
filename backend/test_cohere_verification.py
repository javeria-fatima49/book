"""
Simple verification script to test that Cohere embeddings with caching are working properly.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.services.rag_service import RagService

async def test_cohere_embeddings_with_caching():
    """
    Test that Cohere embeddings are working properly with caching.
    """
    print("Testing Cohere embeddings with caching in RAG pipeline...")

    try:
        # Initialize RAG service (this will use Cohere for embeddings with caching)
        rag_service = RagService()
        print("✓ RAG Service initialized successfully with Cohere embeddings")

        # Check that the embedding model is set correctly
        print(f"✓ Embedding model: {rag_service.embedding_model}")
        print(f"✓ LLM model: {rag_service.llm_model}")

        # Test embedding generation
        test_text = "Artificial Intelligence and Machine Learning are fascinating fields"
        embedding = await rag_service._get_text_embedding(test_text)

        print(f"✓ Cohere embedding generated successfully")
        print(f"  Text: {test_text[:50]}...")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")

        # Test that the embedding is a list of floats
        assert isinstance(embedding, list), "Embedding should be a list"
        assert all(isinstance(val, (int, float)) for val in embedding), "All embedding values should be numbers"
        print("✓ Embedding structure is correct")

        # Verify that caching is working by getting the same embedding again
        print("\nTesting embedding caching...")
        embedding2 = await rag_service._get_text_embedding(test_text)
        print(f"✓ Cached embedding has same length: {len(embedding2)}")
        
        # Verify the embeddings are identical
        assert embedding == embedding2, "Cached embedding should match original"
        print("✓ Caching works correctly - same embedding retrieved from cache")

        # Test upsert functionality with the new embedding size
        metadata = {"chapter_title": "Test Chapter", "book_title": "Test Book", "book_author": "Test Author"}
        upserted_count = await rag_service.upsert_embeddings("This is a test content for the Cohere RAG system.", metadata)
        print(f"✓ Successfully upserted {upserted_count} embeddings to Qdrant with Cohere embeddings")

        print("\n✓ All Cohere embedding with caching tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during Cohere embedding test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running Cohere Embedding with Caching Verification")
    print("=" * 60)

    success = asyncio.run(test_cohere_embeddings_with_caching())

    if success:
        print("\n✓ Cohere embeddings with caching are working properly!")
    else:
        print("\n✗ Cohere embeddings with caching test failed!")
        exit(1)