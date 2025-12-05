from pydantic import BaseModel, Field
from typing import Optional


class TranslateRequest(BaseModel):
    """
    Represents a request to translate text.
    Attributes:
        content (str): The text content to be translated.
        target_language (str): The target language code (e.g., "ur" for Urdu).
        source_language (Optional[str]): The source language code (e.g., "en" for English).
                                         Defaults to English if not provided.
    """

    content: str = Field(min_length=1, description="The text content to be translated.")
    target_language: str = Field(
        min_length=1, max_length=5, description="The target language code (e.g., 'ur')."
    )
    source_language: Optional[str] = Field(
        None,
        min_length=1,
        max_length=5,
        description="The source language code (e.g., 'en').",
    )


class TranslateResponse(BaseModel):
    """
    Represents the response containing the translated text.
    Attributes:
        translated_content (str): The translated text content.
    """

    translated_content: str
