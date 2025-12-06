import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from backend.src.main import app
from backend.src.services.rag_service import RagService
from backend.src.models.rag_models import RagQueryResponse, Source
from backend.src.api.rag import get_rag_service

# Create a mock RagService
mock_rag_service = AsyncMock(spec=RagService)

# Dependency override for RagService
def get_mock_rag_service_override():
    return mock_rag_service

app.dependency_overrides[get_rag_service] = get_mock_rag_service_override

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test."""
    mock_rag_service.reset_mock()

def test_rag_query_success():
    """Test successful RAG query."""
    mock_rag_service.query_rag.return_value = RagQueryResponse(
        answer="This is a test answer.",
        sources=[Source(text="source text", metadata={"chapter": "1"})]
    )
    
    response = client.post("/api/v1/query", json={"query": "test query"})
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["answer"] == "This is a test answer."
    assert len(json_response["sources"]) == 1
    assert json_response["sources"][0]["text"] == "source text"
    mock_rag_service.query_rag.assert_called_once()

def test_rag_query_failure():
    """Test failing RAG query."""
    mock_rag_service.query_rag.side_effect = Exception("RAG query failed")
    
    response = client.post("/api/v1/query", json={"query": "test query"})
    
    assert response.status_code == 500
    # The detail is now a dict from the exception handler
    assert "Internal server error" in response.json()["message"]
    mock_rag_service.query_rag.assert_called_once()

def test_embeddings_upsert_success():
    """Test successful embeddings upsert."""
    mock_rag_service.upsert_embeddings.return_value = 1
    
    test_content = "This is some test content for embedding."
    test_metadata = {"chapter_title": "Test Chapter", "section_id": "1.1"}
    response = client.post(
        "/api/v1/embeddings/upsert",
        json={"content": test_content, "metadata": test_metadata}
    )
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["upserted_count"] == 1
    mock_rag_service.upsert_embeddings.assert_called_once()

def test_embeddings_upsert_failure():
    """Test failing embeddings upsert."""
    mock_rag_service.upsert_embeddings.side_effect = Exception("Upsert failed")
    
    test_content = "This is some test content for embedding."
    test_metadata = {"chapter_title": "Test Chapter", "section_id": "1.1"}
    response = client.post(
        "/api/v1/embeddings/upsert",
        json={"content": test_content, "metadata": test_metadata}
    )
    
    assert response.status_code == 500
    # The detail is now a dict from the exception handler
    assert "Internal server error" in response.json()["message"]
    mock_rag_service.upsert_embeddings.assert_called_once()
