import pytest
from unittest.mock import AsyncMock, patch
from backend.src.services.rag_service import RagService
from backend.src.models.rag_models import RagQueryRequest

@patch('backend.src.services.rag_service.get_qdrant_client')
@patch('backend.src.services.rag_service.openai.OpenAI')
@patch('backend.src.services.rag_service.OPENAI_API_KEY', 'test_key')
def test_rag_service_initialization_success(mock_openai, mock_get_qdrant):
    """Test successful RagService initialization."""
    service = RagService()
    assert service.openai_client is not None
    assert service.qdrant_client is not None
    mock_openai.assert_called_with(api_key='test_key')
    mock_get_qdrant.assert_called_once()

@patch('backend.src.services.rag_service.OPENAI_API_KEY', None)
def test_rag_service_initialization_no_api_key():
    """Test RagService initialization fails if OPENAI_API_KEY is not set."""
    with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
        RagService()

@pytest.mark.asyncio
@patch('backend.src.services.rag_service.OPENAI_API_KEY', 'test_key')
async def test_query_rag_success():
    """Test a successful RAG query."""
    with patch('backend.src.services.rag_service.get_qdrant_client'), \
         patch('backend.src.services.rag_service.openai.OpenAI'):
        service = RagService()

        # Mock dependencies
        service.openai_client.embeddings.create = AsyncMock(return_value=AsyncMock(data=[AsyncMock(embedding=[0.1, 0.2])]))
        service.qdrant_client.search = AsyncMock(return_value=[AsyncMock(payload={"text": "relevant text", "metadata": {}})])
        service.openai_client.chat.completions.create = AsyncMock(return_value=AsyncMock(choices=[AsyncMock(message=AsyncMock(content="LLM answer"))]))

        request = RagQueryRequest(query="test query")
        response = await service.query_rag(request)

        assert response.answer == "LLM answer"
        assert len(response.sources) == 1
        assert response.sources[0].text == "relevant text"

@pytest.mark.asyncio
@patch('backend.src.services.rag_service.OPENAI_API_KEY', 'test_key')
async def test_query_rag_no_context_found():
    """Test RAG query when no relevant context is found."""
    with patch('backend.src.services.rag_service.get_qdrant_client'), \
         patch('backend.src.services.rag_service.openai.OpenAI'):
        service = RagService()

        # Mock dependencies
        service.openai_client.embeddings.create = AsyncMock(return_value=AsyncMock(data=[AsyncMock(embedding=[0.1, 0.2])]))
        service.qdrant_client.search = AsyncMock(return_value=[]) # No results

        request = RagQueryRequest(query="test query")
        response = await service.query_rag(request)

        assert "could not find relevant information" in response.answer
        assert len(response.sources) == 0

@pytest.mark.asyncio
@patch('backend.src.services.rag_service.OPENAI_API_KEY', 'test_key')
async def test_upsert_embeddings_success_collection_exists():
    """Test successful upserting of embeddings when collection already exists."""
    with patch('backend.src.services.rag_service.get_qdrant_client'), \
         patch('backend.src.services.rag_service.openai.OpenAI'):
        service = RagService()

        # Mock dependencies
        service.openai_client.embeddings.create = AsyncMock(return_value=AsyncMock(data=[AsyncMock(embedding=[0.1, 0.2])]))
        service.qdrant_client.upsert = AsyncMock()
        service.qdrant_client.get_collection = AsyncMock()
        service.qdrant_client.create_collection = AsyncMock()

        count = await service.upsert_embeddings("test content", {"chapter": "1"})

        assert count == 1
        service.qdrant_client.get_collection.assert_called_once()
        service.qdrant_client.create_collection.assert_not_called()
        service.qdrant_client.upsert.assert_called_once()

@pytest.mark.asyncio
@patch('backend.src.services.rag_service.OPENAI_API_KEY', 'test_key')
async def test_upsert_embeddings_success_collection_does_not_exist():
    """Test successful upserting of embeddings when collection does not exist."""
    with patch('backend.src.services.rag_service.get_qdrant_client'), \
         patch('backend.src.services.rag_service.openai.OpenAI'):
        service = RagService()

        # Mock dependencies
        service.openai_client.embeddings.create = AsyncMock(return_value=AsyncMock(data=[AsyncMock(embedding=[0.1, 0.2])]))
        service.qdrant_client.upsert = AsyncMock()
        service.qdrant_client.get_collection = AsyncMock(side_effect=Exception("Collection not found"))
        service.qdrant_client.create_collection = AsyncMock()

        count = await service.upsert_embeddings("test content", {"chapter": "1"})

        assert count == 1
        service.qdrant_client.get_collection.assert_called_once()
        service.qdrant_client.create_collection.assert_called_once()
        service.qdrant_client.upsert.assert_called_once()
