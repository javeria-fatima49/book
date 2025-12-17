"""
Database models for chat logs and user interactions.
Defines SQLAlchemy models to store user queries and AI responses in Neon database.
"""

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ChatLog(Base):
    """
    Model representing a chat interaction log between user and AI.
    Stores user queries and AI responses along with timestamps.
    
    Attributes:
        id (int): Primary key identifier (auto-incremented)
        user_query (str): The user's question/query to the AI
        ai_answer (str): The AI-generated response to the user's query  
        created_at (datetime): Timestamp when the chat log was created (auto-generated)
    """
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)  # Store the user's query
    ai_answer = Column(Text, nullable=False)   # Store the AI's response
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-generated timestamp