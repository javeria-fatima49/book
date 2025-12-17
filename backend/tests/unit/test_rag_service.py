import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.rag_service import RagService
from src.models.rag_models import RagQueryRequest

@patch('src.services.rag_service.get_qdrant_client')
@patch('src.services.rag_service.cohere')
@patch('src.services.rag_service.COHERE_API_KEY', 'test_key')
def test_rag_service_initialization_success(mock_cohere, mock_get_qdrant):
    """Test successful RagService initialization."""
    service = RagService()
    assert service.cohere_client is not None
    assert service.qdrant_client is not None
    # Check that Cohere client was initialized (the constructor is called)
    mock_cohere.AsyncClient.assert_called_with('test_key')
    mock_get_qdrant.assert_called_once()

@patch('src.services.rag_service.COHERE_API_KEY', None)
def test_rag_service_initialization_no_api_key():
    """Test RagService initialization fails if COHERE_API_KEY is not set."""
    with pytest.raises(ValueError, match="COHERE_API_KEY is not set"):
        RagService()

@pytest.mark.asyncio
@patch('src.services.rag_service.COHERE_API_KEY', 'test_key')
@patch('src.services.rag_service.GEMINI_API_KEY', 'test_key')
async def test_query_rag_success():
    """Test a successful RAG query."""
    with patch('src.services.rag_service.get_qdrant_client'), \
         patch('src.services.rag_service.cohere.AsyncClient') as mock_cohere_client, \
         patch('src.services.rag_service.genai') as mock_genai:

        # Setup Gemini mock for LLM
        mock_gemini_model = AsyncMock()
        mock_generation_config = AsyncMock()
        mock_gemini_response = AsyncMock()
        mock_candidate = AsyncMock()
        mock_part = AsyncMock()

        mock_gemini_response.candidates = [mock_candidate]
        mock_candidate.content = AsyncMock()
        mock_candidate.content.parts = [mock_part]
        mock_part.text = "LLM answer"

        # Mock the _validate_query_relevance to return True so the query isn't blocked
        with patch.object(RagService, '_validate_query_relevance', return_value=True):
            mock_gemini_model.generate_content = AsyncMock(return_value=mock_gemini_response)
            mock_genai.GenerativeModel = lambda x: mock_gemini_model

            # Setup Cohere mock for embeddings
            mock_embed_response = AsyncMock()
            mock_embed_response.embeddings = [[0.1, 0.2]]  # Two-dimensional because Cohere returns list of embeddings
            mock_cohere_client.return_value.embed = AsyncMock(return_value=mock_embed_response)

            service = RagService()
            service.gemini_client = mock_genai
            service.llm = mock_gemini_model

            # Mock dependencies - use regular Mock for synchronous Qdrant methods
            mock_search_hit = Mock()
            mock_search_hit.payload = {"text": "relevant text", "metadata": {}}
            mock_search_hit.score = 0.5  # A score above the threshold of 0.3

            # Create mock search result with points attribute
            mock_search_result = Mock()
            mock_search_result.points = [mock_search_hit]
            service.qdrant_client.query_points = Mock(return_value=mock_search_result)

            request = RagQueryRequest(query="What is artificial intelligence?")
            response = await service.query_rag(request)

            assert response.answer == "LLM answer"
            assert len(response.sources) == 1
            assert response.sources[0].text == "relevant text"

@pytest.mark.asyncio
@patch('src.services.rag_service.COHERE_API_KEY', 'test_key')
@patch('src.services.rag_service.GEMINI_API_KEY', 'test_key')
async def test_query_rag_no_context_found():
    """Test RAG query when no relevant context is found."""
    with patch('src.services.rag_service.get_qdrant_client'), \
         patch('src.services.rag_service.cohere.AsyncClient') as mock_cohere_client, \
         patch('src.services.rag_service.genai') as mock_genai:

        # Setup Gemini mock for LLM
        mock_gemini_model = AsyncMock()
        mock_generation_config = AsyncMock()
        mock_gemini_response = AsyncMock()
        mock_candidate = AsyncMock()
        mock_part = AsyncMock()

        mock_gemini_response.candidates = [mock_candidate]
        mock_candidate.content = AsyncMock()
        mock_candidate.content.parts = [mock_part]
        mock_part.text = "LLM answer"

        # Mock the _validate_query_relevance to return True so the query isn't blocked
        with patch.object(RagService, '_validate_query_relevance', return_value=True):
            mock_gemini_model.generate_content = AsyncMock(return_value=mock_gemini_response)
            mock_genai.GenerativeModel = lambda x: mock_gemini_model

            # Setup Cohere mock for embeddings
            mock_embed_response = AsyncMock()
            mock_embed_response.embeddings = [[0.1, 0.2]]
            mock_cohere_client.return_value.embed = AsyncMock(return_value=mock_embed_response)

            service = RagService()
            service.gemini_client = mock_genai
            service.llm = mock_gemini_model

            # Mock dependencies - use regular Mock for synchronous Qdrant methods
            # Create mock search result with empty points list
            mock_search_result = Mock()
            mock_search_result.points = []
            service.qdrant_client.query_points = Mock(return_value=mock_search_result)

            request = RagQueryRequest(query="What is artificial intelligence?")
            response = await service.query_rag(request)

            assert "could not find relevant information" in response.answer
            assert len(response.sources) == 0

@pytest.mark.asyncio
@patch('src.services.rag_service.COHERE_API_KEY', 'test_key')
@patch('src.services.rag_service.GEMINI_API_KEY', 'test_key')
async def test_upsert_embeddings_success_collection_exists():
    """Test successful upserting of embeddings when collection already exists."""
    with patch('src.services.rag_service.get_qdrant_client'), \
         patch('src.services.rag_service.cohere.AsyncClient') as mock_cohere_client, \
         patch('src.services.rag_service.genai') as mock_genai:

        # Setup Cohere mock for embeddings
        mock_embed_response = AsyncMock()
        mock_embed_response.embeddings = [[0.1, 0.2]]
        mock_cohere_client.return_value.embed = AsyncMock(return_value=mock_embed_response)

        service = RagService()

        service.qdrant_client.upsert = Mock()
        service.qdrant_client.get_collection = Mock()
        service.qdrant_client.create_collection = Mock()

        count = await service.upsert_embeddings("test content", {"chapter": "1"})

        assert count == 1
        service.qdrant_client.get_collection.assert_called_once()
        service.qdrant_client.create_collection.assert_not_called()
        service.qdrant_client.upsert.assert_called_once()

@pytest.mark.asyncio
@patch('src.services.rag_service.COHERE_API_KEY', 'test_key')
@patch('src.services.rag_service.GEMINI_API_KEY', 'test_key')
async def test_upsert_embeddings_success_collection_does_not_exist():
    """Test successful upserting of embeddings when collection does not exist."""
    with patch('src.services.rag_service.get_qdrant_client'), \
         patch('src.services.rag_service.cohere.AsyncClient') as mock_cohere_client, \
         patch('src.services.rag_service.genai') as mock_genai:

        # Setup Cohere mock for embeddings
        mock_embed_response = AsyncMock()
        mock_embed_response.embeddings = [[0.1, 0.2]]
        mock_cohere_client.return_value.embed = AsyncMock(return_value=mock_embed_response)

        service = RagService()

        service.qdrant_client.upsert = Mock()
        service.qdrant_client.get_collection = Mock(side_effect=Exception("Collection not found"))
        service.qdrant_client.create_collection = Mock()

        count = await service.upsert_embeddings("test content", {"chapter": "1"})

        assert count == 1
        service.qdrant_client.get_collection.assert_called_once()
        service.qdrant_client.create_collection.assert_called_once()
        service.qdrant_client.upsert.assert_called_once()
