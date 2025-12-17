import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
NEONDB_CONNECTION_STRING = os.getenv("NEONDB_CONNECTION_STRING") or os.getenv("NEON_DB_URL")
REDIS_URL = os.getenv("REDIS_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Use a default or None if not set, to handle startup without DB
NEONDB_CONNECTION_STRING = NEONDB_CONNECTION_STRING or os.getenv("DATABASE_URL") or None