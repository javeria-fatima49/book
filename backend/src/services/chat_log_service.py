"""
Service for managing chat logs in the Neon database.
Handles saving user queries and AI responses to the chat_logs table.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from datetime import datetime
import logging
from typing import Optional

from src.models.chat_models import ChatLog

logger = logging.getLogger(__name__)


class ChatLogService:
    """
    Service for handling chat log operations in the database.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the ChatLogService with a database session.
        
        Args:
            db (AsyncSession): The async database session to use for operations
        """
        self.db = db

    async def save_chat_log(self, user_query: str, ai_answer: str) -> Optional[int]:
        """
        Save a user query and AI response to the chat_logs table.
        
        Args:
            user_query (str): The user's question/query
            ai_answer (str): The AI-generated response
            
        Returns:
            Optional[int]: The ID of the created chat log entry, or None if unsuccessful
        """
        try:
            logger.info(f"Saving chat log to database: user_query (first 50 chars): {user_query[:50]}...")
            
            # Create a new ChatLog instance
            chat_log = ChatLog(
                user_query=user_query,
                ai_answer=ai_answer,
                created_at=datetime.utcnow()
            )
            
            # Add the chat log to the session and commit
            self.db.add(chat_log)
            await self.db.commit()
            await self.db.refresh(chat_log)
            
            logger.info(f"Successfully saved chat log with ID: {chat_log.id}")
            return chat_log.id
            
        except Exception as e:
            logger.error(f"Error saving chat log to database: {e}", exc_info=True)
            # Rollback the transaction in case of error
            await self.db.rollback()
            return None