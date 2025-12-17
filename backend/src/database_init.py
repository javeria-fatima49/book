"""
Database initialization script for Neon PostgreSQL.
Creates all required tables for the application.
"""

import asyncio
import logging
from src.core.database import create_tables

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize all database tables."""
    logger.info("Initializing database tables...")
    try:
        await create_tables()
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(init_db())