import openai
from qdrant_client import models
from typing import List
import logging
from fastapi import HTTPException

from backend.src.core.config import OPENAI_API_KEY
from backend.src.core.qdrant import get_qdrant_client
from backend.src.models.rag_models import Source, RagQueryRequest, RagQueryResponse

logger = logging.getLogger(__name__)


class RagService:
    """
    Service class for Retrieval-Augmented Generation (RAG) operations.
    Handles embedding generation, Qdrant interaction, and LLM answer generation.
    """

    def __init__(self):
        """
        Initializes the RagService with OpenAI and Qdrant clients,
        and defines the embedding and LLM models to be used.
        Raises:
            ValueError: If OPENAI_API_KEY is not set in environment variables.
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")

        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.qdrant_client = get_qdrant_client()
        self.embedding_model = "text-embedding-3-small"
        self.llm_model = "gpt-4"  # Or another suitable LLM

    async def _get_text_embedding(self, text: str) -> List[float]:
        """
        Generates embeddings for a given text using OpenAI's embedding model.
        Args:
            text (str): The input text to be embedded.
        Returns:
            List[float]: A list of floats representing the embedding vector.
        """
        response = await self.openai_client.embeddings.create(
            input=text, model=self.embedding_model
        )
        return response.data[0].embedding

    async def query_rag(self, request: RagQueryRequest) -> RagQueryResponse:
        """
        Processes a RAG query:
        1. Embeds the user's query.
        2. Performs a semantic search in Qdrant to retrieve relevant content.
        3. Generates an answer using an LLM based on the retrieved content and user's query.
        Args:
            request (RagQueryRequest): The request object containing the user's query and optional user_id.
        Returns:
            RagQueryResponse: The response object containing the AI-generated answer and sources.
        Raises:
            HTTPException: If there's an error generating the LLM response.
        """
        logger.info(f"Processing RAG query for user {request.user_id}: {request.query}")

        # 1. Embed the user's query
        query_embedding = await self._get_text_embedding(request.query)

        # 2. Perform semantic search in Qdrant
        search_result = await self.qdrant_client.search(
            collection_name="textbook_embeddings",  # Defined in spec
            query_vector=query_embedding,
            limit=5,  # Retrieve top 5 relevant documents
            # TODO: Consider tuning `limit` and `score_threshold` for optimal relevance and performance
            with_payload=True,
        )

        context_parts = []
        sources = []
        for hit in search_result:
            if hit.payload and "text" in hit.payload:
                context_parts.append(hit.payload["text"])
                sources.append(Source(text=hit.payload["text"], metadata=hit.payload))

        if not context_parts:
            logger.warning(f"No relevant context found for query: {request.query}")
            return RagQueryResponse(
                answer=(
                    "I could not find relevant information in the textbook to answer"
                    " your question. Please try rephrasing it."
                ),
                sources=[],
            )

        context = "\n\n".join(context_parts)

        # 3. Generate answer using LLM
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions based on the"
                    " provided textbook content. Cite your sources by referring to the"
                    " provided text snippets."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context: {context}\n\nQuestion: {request.query}\n\nAnswer:"
                ),
            },
        ]

        try:
            llm_response = await self.openai_client.chat.completions.create(
                model=self.llm_model, messages=messages, temperature=0.7, max_tokens=500
            )
            answer = llm_response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Re-raising as HTTPException is handled at API level
            raise HTTPException(status_code=500, detail="Error generating answer.")

        return RagQueryResponse(answer=answer, sources=sources)

    async def upsert_embeddings(self, content: str, metadata: dict) -> int:
        """
        Generates embeddings for content and upserts them to Qdrant.
        Args:
            content (str): The textbook content to be embedded.
            metadata (dict): Metadata associated with the content.
        Returns:
            int: The number of embeddings successfully upserted.
        """
        logger.info(
            "Upserting embeddings for content with metadata:"
            f" {metadata.get('chapter_title')}"
        )

        # TODO: Implement chunking logic here if content is too large
        # For now, assumes content is a single chunk
        text_chunk = content
        embedding = await self._get_text_embedding(text_chunk)

        points = [
            models.PointStruct(
                id=str(
                    hash(text_chunk)
                ),  # Simple hash for ID, consider UUID or persistent ID
                vector=embedding,
                payload={"text": text_chunk, **metadata},
            )
        ]

        # Ensure collection exists (or create it if it doesn't)
        self.qdrant_client.create_collection(
            collection_name="textbook_embeddings",
            vectors_config=models.VectorParams(
                size=1536, distance=models.Distance.COSINE
            ),
            on_existent_collection=models.OnExistentCollection.DoNothing,
        )

        response = await self.qdrant_client.upsert(
            collection_name="textbook_embeddings",
            points=points,
            wait=True,
        )
        logger.info(f"Qdrant upsert response: {response}")
        return len(points)
