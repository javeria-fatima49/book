from redis.asyncio import Redis # Still use async Redis client class
from src.core.config import REDIS_URL
import logging

logger = logging.getLogger(__name__)


def get_redis_client() -> Redis: # Not async def
    """Initializes and returns an asynchronous Redis client."""
    if not REDIS_URL:
        raise ValueError("REDIS_URL must be set in environment variables.")

    try:
        client = Redis.from_url(REDIS_URL, decode_responses=True)
        # Ping will be handled in a startup event if needed, or by FastAPILimiter
        logger.info("Asynchronous Redis client initialized (connection not yet verified).")
    except Exception as e:
        logger.error(f"Error initializing Redis client: {e}")
        raise
    return client
