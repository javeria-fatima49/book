"""Summary skill for condensing documents."""

import asyncio
import logging
from typing import Any, Dict
from transformers import pipeline

from src.subagents import BaseSkill, SkillResult, SkillResultStatus

logger = logging.getLogger(__name__)


class SummarySkill(BaseSkill):
    """Skill to condense long documents into key points with customizable length."""

    def __init__(self):
        super().__init__(
            name="summary",
            description="Condenses long documents into key points with customizable length"
        )
        # Initialize Hugging Face summarization pipeline
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            logger.warning(f"Failed to initialize summarizer: {e}. Using fallback method.")
            self.summarizer = None

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        Execute summary skill.
        Expected input_data keys: 'text', 'max_length', 'min_length'
        """
        try:
            # Validate input
            if not await self.validate_input(input_data):
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    data="Invalid input data"
                )

            # Preprocess input
            processed_data = await self.preprocess(input_data)
            text = processed_data['text']
            max_length = processed_data.get('max_length', 150)
            min_length = processed_data.get('min_length', 50)

            # Perform summarization
            if len(text.split()) < 50:  # Too short to summarize
                summary = text
            else:
                if self.summarizer is None:
                    # Fallback: return first few sentences
                    sentences = text.split('. ')
                    summary = '. '.join(sentences[:3]) + '.'
                else:
                    # Split long text into chunks if needed
                    if len(text) > 1024:
                        # For very long texts, summarize in chunks and then summarize the summaries
                        chunks = self._split_text(text, chunk_size=1000)
                        chunk_summaries = []

                        for chunk in chunks:
                            try:
                                result = self.summarizer(
                                    chunk,
                                    max_length=max_length,
                                    min_length=min_length,
                                    do_sample=False
                                )
                                chunk_summaries.append(result[0]['summary_text'])
                            except Exception as e:
                                logger.error(f"Error summarizing chunk: {e}")
                                chunk_summaries.append(chunk[:max_length])

                        # Summarize the summaries
                        combined_summary = ' '.join(chunk_summaries)
                        result = self.summarizer(
                            combined_summary,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=False
                        )
                        summary = result[0]['summary_text']
                    else:
                        result = self.summarizer(
                            text,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=False
                        )
                        summary = result[0]['summary_text']

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                data={
                    'original_length': len(text),
                    'summary_length': len(summary),
                    'summary': summary,
                    'compression_ratio': len(summary) / len(text)
                },
                metadata={'processing_time': asyncio.get_event_loop().time()}
            )
        except Exception as e:
            logger.error(f"Error in Summary Skill: {e}")
            return SkillResult(
                status=SkillResultStatus.ERROR,
                data=str(e)
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for summary skill"""
        return (
            'text' in input_data and
            isinstance(input_data['text'], str) and
            len(input_data['text']) > 0
        )

    def _split_text(self, text: str, chunk_size: int) -> list[str]:
        """Split text into chunks of approximately chunk_size words"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# Register the skill
from src.subagents import skill_registry
skill_registry.register_skill(SummarySkill())