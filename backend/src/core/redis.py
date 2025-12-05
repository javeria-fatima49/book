from redis import Redis
from backend.src.core.config import REDIS_URL
import logging

logger = logging.getLogger(__name__)


def get_redis_client() -> Redis:
    """Initializes and returns a Redis client."""
    if not REDIS_URL:
        raise ValueError("REDIS_URL must be set in environment variables.")

    try:
        client = Redis.from_url(REDIS_URL, decode_responses=True)
        # Ping to check connection
        client.ping()
        logger.info("Successfully connected to Redis.")
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        raise
    return client
