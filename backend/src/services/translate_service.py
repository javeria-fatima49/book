from backend.src.models.translate_models import TranslateRequest, TranslateResponse
from backend.src.core.redis import get_redis_client
from backend.src.core.config import (
    OPENAI_API_KEY,
)  # Assuming OpenAI can be used for translation or another key
import logging
import openai  # Using OpenAI as a placeholder for AI translation service

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service class for handling translation operations.
    Utilizes an AI translation service and Redis for caching translated content.
    """

    def __init__(self):
        """
        Initializes the TranslationService with Redis and OpenAI clients.
        Assumes OPENAI_API_KEY is available for the mock AI translation.
        """
        self.redis_client = get_redis_client()
        # Using OpenAI as a placeholder for actual translation API like Google Translate
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
            # Using OpenAI Chat Completion as a mock translation service
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using a powerful model for good mock translation
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"Translate the following English text to {target_language}."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            translated_text = response.choices[0].message.content.strip()
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
        cached_translation = self.redis_client.get(cache_key)
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
        self.redis_client.set(
            cache_key, translated_text, ex=3600
        )  # Cache for 1 hour # TODO: Tune cache expiration (ex) based on content freshness and usage patterns.
        logger.info(f"Translation stored in cache for key: {cache_key}")

        return TranslateResponse(translated_content=translated_text)
