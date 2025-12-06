from fastapi import APIRouter, Depends, HTTPException, status
from src.models.translate_models import TranslateRequest, TranslateResponse
from src.services.translate_service import TranslationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency to get TranslationService instance
def get_translation_service() -> TranslationService:
    """
    Dependency function that provides a TranslationService instance.
    """
    return TranslationService()


@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(
    request: TranslateRequest,
    translation_service: TranslationService = Depends(get_translation_service),
):
    """
    Handles translation requests, translating content to the target language and
    returning the result.
    """
    logger.info(
        f"Received translation request for content (first 50 chars): '{request.content[:50]}...'"
        f" to language: {request.target_language}"
    )
    try:
        response = await translation_service.translate_content(request)
        logger.info("Translation successful.")
        return response
    except ValueError as e:
        logger.error(f"Bad request for translation: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Internal server error during translation.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
