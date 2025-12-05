import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
NEONDB_CONNECTION_STRING = os.getenv("NEONDB_CONNECTION_STRING")
REDIS_URL = os.getenv("REDIS_URL")
