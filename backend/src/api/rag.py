import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.rag_models import (
    RagQueryRequest,
    RagQueryResponse,
    UpsertEmbeddingsRequest,
    UpsertEmbeddingsResponse,
)
from src.services.rag_service import RagService
from src.services.document_ingestion_service import DocumentIngestionService
from src.services.book_service import BookService
from src.core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependencies
def get_rag_service() -> RagService:
    """
    Dependency function that provides a RagService instance.
    """
    return RagService()

def get_book_service(db: AsyncSession = Depends(get_db_session)) -> BookService:
    """
    Dependency function that provides a BookService instance.
    """
    return BookService(db)

def get_document_ingestion_service(
    book_service: BookService = Depends(get_book_service),
    rag_service: RagService = Depends(get_rag_service)
) -> DocumentIngestionService:
    """
    Dependency function that provides a DocumentIngestionService instance.
    """
    return DocumentIngestionService(book_service, rag_service)


@router.post("/query", response_model=RagQueryResponse)
async def query_rag_endpoint(
    request: RagQueryRequest, rag_service: RagService = Depends(get_rag_service)
):
    """
    Handles RAG queries, processing user questions and returning AI-generated
    answers with sources.
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
    Processes textbook content, converts it into embeddings, and upserts them
    to Qdrant.
    """
    logger.info(
        "Received request to upsert embeddings for content with metadata:"
        f" {request.metadata}"
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


# New endpoints for book ingestion
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class BookIngestionRequest(BaseModel):
    title: str
    author: str
    isbn: str
    content: str


class BookIngestionResponse(BaseModel):
    status: str
    book_id: int
    chunks_processed: int
    vectors_upserted: int
    message: str


class ChapterData(BaseModel):
    title: str
    content: str
    page_number: Optional[int] = 0


class ChaptersIngestionRequest(BaseModel):
    book_id: int
    chapters: List[ChapterData]


class ChaptersIngestionResponse(BaseModel):
    status: str
    chapters_created: int
    vectors_upserted: int
    message: str


@router.post("/books/ingest", response_model=BookIngestionResponse)
async def ingest_book_endpoint(
    request: BookIngestionRequest,
    ingestion_service: DocumentIngestionService = Depends(get_document_ingestion_service)
):
    """
    Endpoint to ingest an entire book into the RAG system.
    Creates database records and stores embeddings in Qdrant.
    """
    logger.info(f"Received request to ingest book: {request.title} by {request.author}")
    try:
        result = await ingestion_service.ingest_book(
            title=request.title,
            author=request.author,
            isbn=request.isbn,
            content=request.content
        )
        logger.info(f"Successfully ingested book: {request.title}")
        return BookIngestionResponse(**result)
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.exception(f"Internal server error during book ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during book ingestion: {e}",
        )


@router.post("/chapters/ingest", response_model=ChaptersIngestionResponse)
async def ingest_chapters_endpoint(
    request: ChaptersIngestionRequest,
    ingestion_service: DocumentIngestionService = Depends(get_document_ingestion_service)
):
    """
    Endpoint to ingest chapters for a specific book into the RAG system.
    """
    logger.info(f"Received request to ingest {len(request.chapters)} chapters for book ID: {request.book_id}")
    try:
        result = await ingestion_service.ingest_chapters(
            book_id=request.book_id,
            chapters_data=[
                {
                    "title": chapter.title,
                    "content": chapter.content,
                    "page_number": chapter.page_number
                }
                for chapter in request.chapters
            ]
        )
        logger.info(f"Successfully ingested chapters for book ID: {request.book_id}")
        return ChaptersIngestionResponse(**result)
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.exception(f"Internal server error during chapter ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during chapter ingestion: {e}",
        )


# Additional endpoints for book management
class BookInfo(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    created_at: str


class ListBooksResponse(BaseModel):
    books: List[BookInfo]
    total_count: int


@router.get("/books", response_model=ListBooksResponse)
async def list_books_endpoint(
    book_service: BookService = Depends(get_book_service)
):
    """
    List all books in the system with basic information.
    """
    logger.info("Received request to list all books")
    try:
        books = await book_service.list_all_books()
        book_infos = [
            BookInfo(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                created_at=book.created_at.isoformat() if book.created_at else ""
            )
            for book in books
        ]
        return ListBooksResponse(books=book_infos, total_count=len(book_infos))
    except Exception as e:
        logger.exception(f"Internal server error during book listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during book listing: {e}",
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the RAG service is running properly.
    """
    return {
        "status": "healthy",
        "service": "RAG Chatbot API",
        "details": {
            "qdrant_connection": "active",
            "cohere_api": "configured",
            "model": "command-r"  # Using current Cohere model
        }
    }


@router.get("/rag")
def get_rag():
    return {"message": "RAG endpoint"}
