"""Search skill for semantic document search."""

import asyncio
import logging
from typing import Any, Dict

from src.subagents import BaseSkill, SkillResult, SkillResultStatus
from src.services.rag_service import RagService

logger = logging.getLogger(__name__)


class SearchSkill(BaseSkill):
    """Skill to perform semantic search across document collections."""

    def __init__(self):
        super().__init__(
            name="search",
            description="Performs semantic search across document collections"
        )
        self.rag_service = RagService()

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        Execute search skill.
        Expected input_data keys: 'query', 'limit', 'filters'
        """
        try:
            if not await self.validate_input(input_data):
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    data="Invalid input data"
                )

            query = input_data['query']
            limit = input_data.get('limit', 5)
            filters = input_data.get('filters', {})

            # Perform semantic search using RAG service
            from src.models.rag_models import RagQueryRequest
            rag_request = RagQueryRequest(query=query, user_id="skill_search")
            
            # We need to adapt the RAG service to work with search-only
            # For this implementation, we'll use the existing RAG service
            search_results = await self._perform_search(query, limit, filters)

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                data={
                    'query': query,
                    'results': search_results,
                    'count': len(search_results)
                },
                metadata={'search_time': asyncio.get_event_loop().time()}
            )
        except Exception as e:
            logger.error(f"Error in Search Skill: {e}")
            return SkillResult(
                status=SkillResultStatus.ERROR,
                data=str(e)
            )

    async def _perform_search(self, query: str, limit: int = 5, filters: dict = None) -> list:
        """Perform the actual search using the RAG service."""
        # This is a simplified version of the search functionality
        # In a complete implementation, we'd use the RAG service properly
        from src.core.qdrant import get_qdrant_client
        from src.services.rag_service import RagService
        
        # Get embedding for the query
        rag_service = RagService()
        query_embedding = await rag_service._get_text_embedding(query)
        
        # Perform search in Qdrant
        client = get_qdrant_client()
        search_result = await client.search(
            collection_name="textbook_embeddings",
            query_vector=query_embedding,
            limit=limit,
            with_payload=True,
        )
        
        # Format results
        results = []
        for hit in search_result:
            if hit.payload and "text" in hit.payload:
                results.append({
                    'text': hit.payload["text"],
                    'metadata': hit.payload,
                    'score': hit.score
                })
        
        return results

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for search skill"""
        return (
            'query' in input_data and
            isinstance(input_data['query'], str) and
            len(input_data['query']) > 0
        )


# Register the skill
from src.subagents import skill_registry
skill_registry.register_skill(SearchSkill())