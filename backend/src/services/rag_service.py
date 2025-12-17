import cohere
from qdrant_client import models
from typing import List
import logging
from fastapi import HTTPException
import hashlib

from src.core.config import COHERE_API_KEY  # Changed from including GEMINI_API_KEY
from src.core.qdrant import get_qdrant_client
from src.core.redis import get_redis_client
from src.models.rag_models import Source, RagQueryRequest, RagQueryResponse
from src.core.database import get_db_session
from src.services.chat_log_service import ChatLogService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CohereModelManager:
    """Manages Cohere model availability with fallback logic."""

    def __init__(self, cohere_client):
        self.cohere_client = cohere_client
        # List of Cohere models in order of preference
        self.model_list = [
            "command-nightly",  # Latest nightly model
            "command-r-plus",   # Most capable model
            "command-r",        # Good capability, newer model
            "command",          # Standard model
            "command-light",    # Lighter, faster model
        ]

    async def test_model_availability(self, model_name: str) -> bool:
        """Test if a specific model is available."""
        try:
            # Simple test call to check model availability
            response = await self.cohere_client.chat(
                model=model_name,
                message="Test message to verify model availability",
                temperature=0.1
            )
            return True
        except Exception as e:
            logger.warning(f"Model {model_name} not available: {e}")
            return False

    async def get_available_model(self) -> str:
        """Get the first available model from the preference list."""
        for model_name in self.model_list:
            if await self.test_model_availability(model_name):
                logger.info(f"Using Cohere model: {model_name}")
                return model_name

        # If no preferred models are available, return command-light as a fallback
        logger.warning("No preferred models available, using command-light as last resort")
        return "command-light"


class RagService:
    """
    Service class for Retrieval-Augmented Generation (RAG) operations.
    Handles embedding generation, Qdrant interaction, and LLM answer generation.
    """

    def __init__(self):
        """
        Initializes the RagService with Cohere and Qdrant clients,
        and defines the embedding and LLM models to be used.
        Raises:
            ValueError: If COHERE_API_KEY is not set in environment variables.
        """
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY is not set in environment variables.")

        self.cohere_client = cohere.AsyncClient(COHERE_API_KEY)  # Initialize Cohere client for both embeddings and LLM
        self.qdrant_client = get_qdrant_client()
        try:
            self.redis_client = get_redis_client()  # Initialize Redis client for embedding caching
        except ValueError:
            # Redis is not configured, set redis_client to None
            self.redis_client = None
            logger.warning("Redis is not configured. Caching will be disabled.")

        # Initialize model manager to handle model availability
        self.model_manager = CohereModelManager(self.cohere_client)
        self.embedding_model = "embed-english-v3.0"  # Cohere embedding model
        # Get available model dynamically
        self.llm_model = "command-r"  # Default model, will be updated dynamically if needed

    async def health_check(self):
        """
        Check if the service dependencies are healthy
        """
        try:
            # Test Qdrant connection
            self.qdrant_client.get_collections()

            # Test embedding generation
            test_embedding = await self._get_text_embedding("test")
            if not test_embedding or len(test_embedding) == 0:
                return False

            # Test LLM model availability
            available_model = await self.model_manager.get_available_model()
            self.llm_model = available_model
            logger.info(f"Using Cohere model: {self.llm_model}")

            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def _get_text_embedding(self, text: str) -> List[float]:
        """
        Generates embeddings for a given text using Cohere's embedding model.
        Uses Redis caching to avoid regenerating embeddings for the same text if Redis is available.
        Args:
            text (str): The input text to be embedded.
        Returns:
            List[float]: A list of floats representing the embedding vector.
        """
        logger.debug(f"Generating embedding for text: {text[:100]}...")  # Log first 100 chars of text
        if self.redis_client:  # Redis is configured
            # Create a cache key based on the text and model
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            cache_key = f"embedding:{self.embedding_model}:{text_hash}"

            try:
                # Try to get embedding from cache first
                cached_embedding = await self.redis_client.get(cache_key)
                if cached_embedding:
                    logger.info(f"Retrieved embedding from cache for text hash: {text_hash[:8]}")
                    embedding = eval(cached_embedding)  # Convert string back to list
                    logger.debug(f"Retrieved cached embedding of length: {len(embedding)}")
                    return embedding

                # If not in cache, generate new embedding
                response = await self.cohere_client.embed(
                    texts=[text],
                    model=self.embedding_model,
                    input_type="search_document"
                )
                embedding = response.embeddings[0]
                logger.debug(f"Generated new embedding of length: {len(embedding)}")

                # Cache the embedding (for 1 hour)
                await self.redis_client.set(cache_key, str(embedding), ex=3600)
                logger.info(f"Cached embedding for text hash: {text_hash[:8]}")

                return embedding
            except Exception as e:
                logger.warning(f"Error in embedding cache operation: {e}")
                # Fallback to direct generation if caching fails
                response = await self.cohere_client.embed(
                    texts=[text],
                    model=self.embedding_model,
                    input_type="search_document"
                )
                embedding = response.embeddings[0]
                logger.debug(f"Generated embedding after cache error, length: {len(embedding)}")
                return embedding
        else:  # Redis is not configured, skip caching
            try:
                response = await self.cohere_client.embed(
                    texts=[text],
                    model=self.embedding_model,
                    input_type="search_document"
                )
                embedding = response.embeddings[0]
                logger.debug(f"Generated embedding without cache, length: {len(embedding)}")
                return embedding
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                # Re-raising the exception as this is crucial for the functionality
                raise

    async def _generate_answer_with_cohere(self, context: str, query: str) -> str:
        """
        Generate answer using Cohere's command-r model based on context and query.
        Args:
            context (str): Retrieved context from Qdrant
            query (str): User's query
        Returns:
            str: The generated answer
        """
        try:
            # Ensure we have an available model before making the call
            available_model = await self.model_manager.get_available_model()
            self.llm_model = available_model

            # Create a detailed prompt for Cohere
            prompt = (
                "You are an expert book assistant that answers questions based on the provided book content. "
                "Your responses must be grounded in the provided context. "
                "If the context does not contain enough information to answer the question, clearly state that by saying 'I don't know'. "
                "Always cite the provided text snippets when forming your answer. "
                "Be accurate and detailed, referencing specific content from the book. "
                "If the user's question is not related to the book content, politely redirect them to ask book-related questions.\n\n"
                f"Book Content Context:\n{context}\n\n"
                f"User Question: {query}\n\n"
                "Provide a comprehensive answer based only on the book content provided above. "
                "Only use information from the context to answer the question. "
                "If the information is not in the context, respond with 'I don't know'."
            )

            logger.debug(f"Sending prompt to Cohere with context length: {len(context)}, query: {query}")

            # Use Cohere's chat functionality with minimal parameters to avoid compatibility issues
            response = await self.cohere_client.chat(
                model=self.llm_model,
                message=prompt,
                temperature=0.3  # Only include essential parameters
            )

            logger.debug(f"Cohere response received: {response.text}")

            # Extract the answer from the response
            if response and response.text:
                answer = response.text.strip()
                logger.debug(f"Cohere generated answer: {answer}")
                # If the answer contains phrases suggesting no information found, return "I don't know"
                if "I don't know" in answer or "no information" in answer.lower() or "not mentioned" in answer.lower():
                    logger.warning(f"Cohere returned knowledge gap: {answer}")
                    return "I don't know"
                return answer
            else:
                logger.warning("Cohere returned empty response")
                return "I don't know"
        except Exception as e:
            logger.error(f"Error generating answer with Cohere: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return a safe default response instead of raising exception to avoid 500 errors
            logger.warning("Returning default response due to Cohere error")
            return "I don't know"

    async def _validate_query_relevance_with_cohere(self, query: str) -> bool:
        """
        Validates if the query is related to book content using Cohere's command-r model.
        Args:
            query (str): The query to validate
        Returns:
            bool: True if query is related to book content, False otherwise
        """
        try:
            # Ensure we have an available model before making the call
            available_model = await self.model_manager.get_available_model()
            model_to_use = available_model  # Don't update self.llm_model just for validation

            prompt = (
                "You are determining if a user's question is related to book content. "
                "A question is considered related to book content if it asks about concepts, "
                "characters, plot, themes, or any topic that would be covered in a published book. "
                "Respond with 'YES' if the question is related to book content, and 'NO' if it's not.\n\n"
                f"Question: {query}\n\n"
                "Related to book content (YES/NO):"
            )

            response = await self.cohere_client.chat(
                model=model_to_use,
                message=prompt,
                temperature=0.1  # Minimal parameters to avoid compatibility issues
            )

            response_text = response.text.strip().upper() if response.text else ""
            return "YES" in response_text or "RELATED" in response_text
        except Exception as e:
            logger.warning(f"Query relevance validation failed with Cohere: {e}")
            # If validation fails, err on the side of allowing the query
            return True

    async def _rewrite_query_for_retrieval(self, original_query: str) -> str:
        """
        Rewrites the user's query to make it more retrieval-friendly by:
        1. Removing contextual references like "from book", "this", etc.
        2. Converting incomplete phrases to complete questions
        3. Improving the query structure for semantic search
        4. Handling documentation-style queries (common in Docusaurus docs)
        """
        import re

        # Store original for logging
        original = original_query.strip()

        # Extract important terms before removing phrases - especially for module-specific queries
        # Look for patterns like "Module X", "Chapter X", etc.
        module_patterns = re.findall(r'(Module\s+\d+|Chapter\s+\d+|Part\s+\d+)', original, re.IGNORECASE)

        # Remove common documentation phrases that don't help with retrieval
        query = re.sub(r'\b(from docs|from documentation|from the docs|from the documentation|in the docs|in documentation)\b', '', original, flags=re.IGNORECASE)

        # Remove common Docusaurus/doc-related phrases, but keep module numbers if present
        query = re.sub(r'\b(this|this topic|this concept|the above|below|as mentioned|refer to)\b', '', query, flags=re.IGNORECASE)

        # Remove common instructional phrases
        query = re.sub(r'\b(explain|describe|what is|what are|tell me about|how to|how do i|define|definition of|overview of)\b', '', query, flags=re.IGNORECASE)

        # Keep module-related terms but clean up the rest
        # If we extracted module patterns, make sure they're preserved in the search
        for pattern in module_patterns:
            # Add module pattern back if it got removed
            if pattern.lower() not in query.lower():
                query = pattern + " " + query

        # Normalize whitespace
        query = ' '.join(query.split())

        # If the resulting query is too short, use the original
        if len(query.strip()) < 3:
            query = original

        logger.debug(f"Query rewritten from '{original}' to '{query}' for retrieval")
        return query.strip()

    async def query_rag(self, request: RagQueryRequest) -> RagQueryResponse:
        """
        Processes a RAG query:
        1. Rewrites and embeds the user's query for better retrieval
        2. Performs a semantic search in Qdrant to retrieve relevant content
        3. Generates an answer using an LLM based on the retrieved content and user's query
        4. Saves the user query and AI response to Neon database
        Args:
            request (RagQueryRequest): The request object containing the user's query and optional user_id
        Returns:
            RagQueryResponse: The response object containing the AI-generated answer and sources
        Raises:
            HTTPException: If there's an error generating the LLM response
        """
        logger.info(f"Processing RAG query for user {request.user_id}: {request.query}")

        # Validate the query is related to book content
        if not await self._validate_query_relevance_with_cohere(request.query):
            logger.warning(f"Query appears unrelated to book content: {request.query}")
            response = RagQueryResponse(
                answer=(
                    "I am a book chatbot designed to answer questions about the book content."
                    " Your question doesn't seem to be related to the book material."
                    " Please ask questions related to the book content."
                ),
                sources=[],
            )

            # Save the query and response to Neon database even for invalid queries
            await self._save_to_database(request.query, response.answer)

            return response

        # 1. Rewrite the query for better retrieval (preserve query intent while removing noise)
        retrieval_query = await self._rewrite_query_for_retrieval(request.query)

        # 2. Embed the rewritten query
        query_embedding = await self._get_text_embedding(retrieval_query)

        # Check if collection exists and has points before querying
        try:
            collection_info = self.qdrant_client.get_collection(collection_name="textbook_embeddings")
            logger.debug(f"Collection info: {collection_info}")
            # Different Qdrant versions have different attribute names for vector count
            if hasattr(collection_info, 'vectors_count'):
                vectors_count = collection_info.vectors_count
            elif hasattr(collection_info, 'point_count'):
                vectors_count = collection_info.point_count
            else:
                vectors_count = "unknown"
            logger.debug(f"Collection vectors count: {vectors_count}")
        except Exception as e:
            logger.error(f"Collection 'textbook_embeddings' may not exist: {e}")
            # Handle case where collection doesn't exist
            response = RagQueryResponse(
                answer="I don't know",  # No content available
                sources=[],
            )
            await self._save_to_database(request.query, response.answer)
            return response

        # 3. Perform semantic search in Qdrant with adjusted parameters
        try:
            search_result = self.qdrant_client.query_points(
                collection_name="textbook_embeddings",  # Ensure correct collection name
                query=query_embedding,
                limit=5,  # Standard top_k of 5
                score_threshold=0.3,  # Return to original threshold for better precision
            )

            logger.debug(f"Qdrant search result: {search_result}")
            logger.debug(f"Number of points returned: {len(search_result.points) if hasattr(search_result, 'points') else 'N/A'}")
        except Exception as e:
            logger.error(f"Error querying Qdrant: {e}")
            # Handle case where query fails
            response = RagQueryResponse(
                answer="I don't know",
                sources=[],
            )
            await self._save_to_database(request.query, response.answer)
            return response

        context_parts = []
        sources = []

        # Log retrieved chunks for debugging (but don't expose to frontend)
        retrieved_chunks_debug = []

        for hit in search_result.points:
            if hit.payload and "text" in hit.payload:
                # Include results with sufficient similarity score and filter out dummy content
                text_content = hit.payload["text"]
                if text_content.strip() != "string" and len(text_content.strip()) > 10:  # Filter out dummy "string" values
                    # Include results with sufficient similarity score
                    if hasattr(hit, 'score') and hit.score >= 0.3:  # Match the score threshold
                        context_parts.append(text_content)
                        # Enhance metadata for better source display
                        enhanced_metadata = hit.payload.copy()
                        enhanced_metadata['relevance_score'] = hit.score
                        sources.append(Source(text=text_content, metadata=enhanced_metadata))
                        retrieved_chunks_debug.append({
                            "score": hit.score,
                            "text_snippet": text_content[:200] + "..." if len(text_content) > 200 else text_content
                        })
                    elif not hasattr(hit, 'score'):  # Compatibility for Qdrant client versions without score attribute
                        context_parts.append(text_content)
                        # Enhance metadata for better source display
                        enhanced_metadata = hit.payload.copy()
                        enhanced_metadata['relevance_score'] = getattr(hit, 'score', 0.0)  # Use 0.0 if no score
                        sources.append(Source(text=text_content, metadata=enhanced_metadata))
                        retrieved_chunks_debug.append({
                            "score": "unknown",
                            "text_snippet": text_content[:200] + "..." if len(text_content) > 200 else text_content
                        })

        logger.debug(f"Retrieved {len(context_parts)} relevant chunks for query '{retrieval_query}': {retrieved_chunks_debug}")

        if not context_parts:
            logger.warning(f"No relevant context found for query: {request.query} (rewritten as: {retrieval_query})")
            # Try with a lower threshold as fallback
            try:
                fallback_search_result = self.qdrant_client.query_points(
                    collection_name="textbook_embeddings",
                    query=query_embedding,
                    limit=8,  # Increase limit for fallback search
                    score_threshold=0.15,  # Lower threshold as fallback
                )

                logger.debug(f"Fallback Qdrant search result: {fallback_search_result}")
                logger.debug(f"Number of fallback points returned: {len(fallback_search_result.points) if hasattr(fallback_search_result, 'points') else 'N/A'}")

                for hit in fallback_search_result.points:
                    if hit.payload and "text" in hit.payload and hit.payload["text"].strip() != "string":
                        # Filter out dummy "string" values and ensure text is meaningful
                        text_content = hit.payload["text"]
                        if len(text_content.strip()) > 10:  # At least 10 characters to be meaningful
                            if (hasattr(hit, 'score') and hit.score >= 0.15) or not hasattr(hit, 'score'):
                                context_parts.append(text_content)
                                # Enhance metadata for better source display
                                enhanced_metadata = hit.payload.copy()
                                enhanced_metadata['relevance_score'] = getattr(hit, 'score', 0.0)
                                sources.append(Source(text=text_content, metadata=enhanced_metadata))
            except Exception as e:
                logger.error(f"Error in fallback querying Qdrant: {e}")

            if not context_parts:
                logger.warning(f"Still no relevant context found with fallback threshold for query: {request.query}")
                response = RagQueryResponse(
                    answer="I don't know",
                    sources=[],
                )

                # Save the query and response to Neon database even when no context found
                await self._save_to_database(request.query, response.answer)

                return response

        context = "\n\n".join(context_parts)

        # 4. Generate answer using Cohere LLM based on context and the original query
        answer = await self._generate_answer_with_cohere(context, request.query)

        # Return answer without sources to remove reference section from frontend
        response = RagQueryResponse(answer=answer, sources=[])

        # Save the user query and AI response to Neon database after successful response generation
        await self._save_to_database(request.query, response.answer)

        return response

    async def _save_to_database(self, user_query: str, ai_answer: str):
        """
        Private helper method to save user query and AI response to the Neon database.

        Args:
            user_query (str): The original user query
            ai_answer (str): The AI-generated response
        """
        try:
            # Create a new async session specifically for saving to the database
            async with get_db_session() as db:
                chat_log_service = ChatLogService(db)
                chat_log_id = await chat_log_service.save_chat_log(user_query, ai_answer)

                if chat_log_id:
                    logger.info(f"Successfully saved chat log to Neon with ID: {chat_log_id}")
                else:
                    logger.warning("Failed to save chat log to Neon database (possibly not configured)")

        except Exception as e:
            logger.warning(f"Error saving chat log to database (this may be expected if database is not configured): {e}")

    async def _validate_query_relevance(self, query: str) -> bool:
        """
        Validates if the query is related to book content before performing RAG lookup.
        This prevents the bot from answering off-topic questions.
        """
        return await self._validate_query_relevance_with_cohere(query)

    async def upsert_embeddings(self, content: str, metadata: dict) -> int:
        """
        Generates embeddings for content and upserts them to Qdrant.
        Args:
            content (str): The textbook content to be embedded.
            metadata (dict): Metadata associated with the content.
        Returns:
            int: The number of embeddings successfully upserted.

        NOTE: For optimal retrieval performance with book content, consider these chunking parameters:
        - Chunk size: 512-1024 tokens (approximately 300-700 words)
        - Overlap: 50-100 tokens to maintain context across chunks
        - Ensure chunks contain complete thoughts/sentences
        """
        logger.info(
            "Upserting embeddings for content with metadata:"
            f" {metadata.get('chapter_title')}"
        )

        # TODO: Implement proper chunking logic here if content is too large
        # Current implementation assumes content is already appropriately chunked
        # For book content, recommended chunking would be:
        # - Size: 512-1024 tokens (approximately 300-700 words)
        # - Overlap: 50-100 tokens to maintain context
        text_chunk = content
        embedding = await self._get_text_embedding(text_chunk)

        points = [
            models.PointStruct(
                id=abs(hash(text_chunk)) % (10**16),  # Ensure positive ID within range
                vector=embedding,
                payload={"text": text_chunk, **metadata},
            )
        ]

        # Ensure collection exists (or create it if it doesn't)
        try:
            self.qdrant_client.get_collection(collection_name="textbook_embeddings")
        except Exception:
            # Note: Cohere embeddings have size 1024 for embed-english-v3.0 model
            self.qdrant_client.create_collection(
                collection_name="textbook_embeddings",
                vectors_config=models.VectorParams(
                    size=1024, distance=models.Distance.COSINE # Changed from 768 to 1024 for Cohere embeddings
                ),
            )

        response = self.qdrant_client.upsert(
            collection_name="textbook_embeddings",
            points=points,
            wait=True,
        )
        logger.info(f"Qdrant upsert response: {response}")
        return len(points)