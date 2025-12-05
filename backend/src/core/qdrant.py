from qdrant_client import QdrantClient
from .config import QDRANT_API_KEY, QDRANT_URL


def get_qdrant_client() -> QdrantClient:
    """Initializes and returns a Qdrant client."""
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError(
            "QDRANT_URL and QDRANT_API_KEY must be set in environment variables."
        )

    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    return client
