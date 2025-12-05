import logging
from fastapi import APIRouter, Depends, HTTPException, status
from backend.src.models.rag_models import (
    RagQueryRequest, RagQueryResponse, UpsertEmbeddingsRequest, UpsertEmbeddingsResponse
)
from backend.src.services.rag_service import RagService

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency to get RagService instance
def get_rag_service() -> RagService:
    """
    Dependency function that provides a RagService instance.
    """
    return RagService()


@router.post("/query", response_model=RagQueryResponse)
async def query_rag_endpoint(
    request: RagQueryRequest, rag_service: RagService = Depends(get_rag_service)
):
    """
    Handles RAG queries, processing user questions and returning AI-generated answers with sources.
    """
    logger.info(f"Received RAG query: {request.query} from user: {request.user_id}")
    try:
        response = await rag_service.query_rag(request)
        logger.info(f"Successfully responded to RAG query for user: {request.user_id}")
        return response
    except ValueError as e:
        logger.error(f"Bad request for RAG query from user {request.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(
            f"Internal server error during RAG query for user {request.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


@router.post("/embeddings/upsert", response_model=UpsertEmbeddingsResponse)
async def upsert_embeddings_endpoint(
    request: UpsertEmbeddingsRequest, rag_service: RagService = Depends(get_rag_service)
):
    """
    Processes textbook content, converts it into embeddings, and upserts them to Qdrant.
    """
    logger.info(
        f"Received request to upsert embeddings for content with metadata: {request.metadata}"
    )
    try:
        upserted_count = await rag_service.upsert_embeddings(
            request.content, request.metadata or {}
        )
        logger.info(f"Successfully upserted {upserted_count} embeddings.")
        return UpsertEmbeddingsResponse(
            status="success",
            message=f"Successfully upserted {upserted_count} embeddings.",
            upserted_count=upserted_count,
        )
    except ValueError as e:
        logger.error(f"Bad request for embeddings upsert: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Internal server error during embeddings upsert.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


@router.get("/rag")
def get_rag():
    return {"message": "RAG endpoint"}
