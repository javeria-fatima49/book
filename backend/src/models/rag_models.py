"""
Pydantic models for RAG (Retrieval-Augmented Generation) feature.
Defines the structure for requests, responses, and related data entities.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class Source(BaseModel):
    """
    Represents a source document or snippet retrieved by the RAG system.
    Attributes:
        text (str): The original text snippet from the source.
        metadata (Dict[str, Any]): A dictionary containing metadata about the source
                                    (e.g., chapter title, URL).
    """

    text: str
    metadata: Dict[str, Any]


class RagQueryRequest(BaseModel):
    """
    Represents a user's query request to the RAG chatbot.
    Attributes:
        query (str): The user's question for the RAG chatbot
                     (minimum length 3 characters).
        user_id (Optional[str]): An optional identifier for the user.
    """

    query: str = Field(
        min_length=3, description="The user's question for the RAG chatbot."
    )
    user_id: Optional[str] = None


class RagQueryResponse(BaseModel):
    """
    Represents the RAG chatbot's response to a user query.
    Attributes:
        answer (str): The AI-generated answer to the user's question.
        sources (List[Source]): A list of source documents or snippets
                                used to generate the answer.
    """

    answer: str
    sources: List[Source]


class UpsertEmbeddingsRequest(BaseModel):
    """
    Represents a request to generate and upsert embeddings for textbook content.
    Attributes:
        content (str): The textbook content to be embedded
                       (minimum length 10 characters).
        metadata (Optional[Dict[str, Any]]): Optional metadata associated with the content.
    """

    content: str = Field(
        min_length=10, description="The textbook content to be embedded."
    )
    metadata: Optional[Dict[str, Any]] = None


class UpsertEmbeddingsResponse(BaseModel):
    """
    Represents the response after successfully upserting embeddings.
    Attributes:
        status (str): The status of the operation (e.g., "success").
        message (str): A descriptive message about the operation's outcome.
        upserted_count (int): The number of vectors successfully upserted.
    """

    status: str
    message: str
    upserted_count: int
