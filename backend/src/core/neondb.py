import psycopg2
from psycopg2 import Error
from .config import NEONDB_CONNECTION_STRING
import logging

logger = logging.getLogger(__name__)


def get_neondb_connection():
    """Establishes and returns a connection to NeonDB."""
    if not NEONDB_CONNECTION_STRING:
        raise ValueError(
            "NEONDB_CONNECTION_STRING must be set in environment variables."
        )

    conn = None
    try:
        conn = psycopg2.connect(NEONDB_CONNECTION_STRING)
        logger.info("Successfully connected to NeonDB.")
    except Error as e:
        logger.error(f"Error connecting to NeonDB: {e}")
        raise
    return conn


def close_neondb_connection(conn):
    """Closes the connection to NeonDB."""
    if conn:
        conn.close()
        logger.info("NeonDB connection closed.")
