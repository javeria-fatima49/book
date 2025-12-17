"""
Test script to verify Cohere embeddings are working properly in the RAG pipeline.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.services.rag_service import RagService

async def test_cohere_embeddings():
    """
    Test that Cohere embeddings are working properly.
    """
    print("Testing Cohere embeddings in RAG pipeline...")
    
    try:
        # Initialize RAG service (this will now use Cohere for embeddings)
        rag_service = RagService()
        print("✓ RAG Service initialized successfully with Cohere embeddings")
        
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
        
        # Test upsert functionality with the new embedding size
        metadata = {"chapter_title": "Test Chapter", "book_title": "Test Book", "book_author": "Test Author"}
        upserted_count = await rag_service.upsert_embeddings("This is a test content for the Cohere RAG system.", metadata)
        print(f"✓ Successfully upserted {upserted_count} embeddings to Qdrant with Cohere embeddings")
        
        print("\n✓ All Cohere embedding tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error during Cohere embedding test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running Cohere Embedding Tests")
    print("=" * 50)
    
    success = asyncio.run(test_cohere_embeddings())
    
    if success:
        print("\n✓ Cohere embeddings are working properly!")
    else:
        print("\n✗ Cohere embeddings test failed!")
        exit(1)