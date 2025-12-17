from src.models.translate_models import TranslateRequest, TranslateResponse
from src.core.redis import get_redis_client
from src.core.config import (
    GEMINI_API_KEY, # Changed from OPENAI_API_KEY
)
import logging
import google.generativeai as genai  # Using Gemini for AI translation service

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service class for handling translation operations.
    Utilizes an AI translation service and Redis for caching translated content.
    """

    def __init__(self):
        """
        Initializes the TranslationService with Redis and Gemini clients.
        Assumes GEMINI_API_KEY is available for the AI translation.
        """
        self.redis_client = get_redis_client()
        genai.configure(api_key=GEMINI_API_KEY)
        self.gemini_client = genai
        self.llm_model = "gemini-1.5-flash"  # Updated Gemini LLM for text generation
        self.llm = genai.GenerativeModel(self.llm_model)

    async def _call_ai_translation_service(
        self, text: str, target_language: str
    ) -> str:
        """
        Calls an AI translation service to translate the given text.
        Currently uses OpenAI's chat completion as a mock.
        Args:
            text (str): The text content to be translated.
            target_language (str): The target language code (e.g., "ur").
        Returns:
            str: The translated text content.
        Raises:
            Exception: If an error occurs during the AI translation service call.
        """
        logger.info(
            f"Calling AI translation service for text: '{text[:50]}...' to"
            f" {target_language}"
        )
        try:
            response = await self.llm.generate_content(
                [
                    f"Translate the following English text to {target_language}:",
                    text
                ]
            )
            translated_text = response.candidates[0].content.parts[0].text.strip()
            logger.info(f"AI translation successful for text: '{text[:50]}...'")
            return translated_text
        except Exception as e:
            logger.error(f"Error calling AI translation service: {e}")
            raise

    async def translate_content(self, request: TranslateRequest) -> TranslateResponse:
        """
        Translates content from source to target language,
        first checking the cache and then calling the AI translation service if needed.
        Args:
            request (TranslateRequest): The request object containing content,
                                         target, and optional source language.
        Returns:
            TranslateResponse: The response object containing the translated text.
        """
        cache_key = (
            f"translation:{request.source_language}-{request.target_language}:"
            f"{hash(request.content)}"
        )

        # Try to retrieve from cache
        cached_translation = await self.redis_client.get(cache_key)
        if cached_translation:
            logger.info(f"Translation retrieved from cache for key: {cache_key}")
            return TranslateResponse(translated_content=cached_translation)

        logger.info(
            f"Cache miss for translation key: {cache_key}. Calling AI translation service."
        )

        # If not in cache, call AI translation service
        translated_text = await self._call_ai_translation_service(
            request.content, request.target_language
        )

        # Store in cache
        await self.redis_client.set(
            cache_key, translated_text, ex=3600
        )  # Cache for 1 hour # TODO: Tune cache expiration (ex) based on content freshness and usage patterns.
        logger.info(f"Translation stored in cache for key: {cache_key}")

        return TranslateResponse(translated_content=translated_text)
