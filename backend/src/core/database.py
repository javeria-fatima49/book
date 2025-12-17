import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .config import NEONDB_CONNECTION_STRING
from src.models.db_models import Base as MainBase  # Existing models
from src.models.chat_models import Base as ChatBase  # New chat log models
import urllib.parse

# Create async engine - using asyncpg driver for Postgres
if NEONDB_CONNECTION_STRING:
    # Parse the connection string and rebuild it without problematic parameters
    parsed = urllib.parse.urlparse(NEONDB_CONNECTION_STRING)

    # Extract components
    scheme = parsed.scheme.replace("postgresql", "postgresql+asyncpg")
    username = parsed.username
    password = parsed.password
    hostname = parsed.hostname
    port = parsed.port or 5432  # Default PostgreSQL port if not specified
    database = parsed.path.lstrip('/')

    # Build the new connection string without problematic parameters
    formatted_connection_string = f"{scheme}://{username}:{password}@{hostname}:{port}/{database}"

    # Handle query parameters carefully for asyncpg compatibility
    # Remove sslmode since asyncpg handles SSL differently
    if parsed.query:
        query_params = urllib.parse.parse_qs(parsed.query)
        # Only include parameters that asyncpg supports - excluding sslmode
        supported_params = ['application_name', 'server_settings']
        filtered_query = []
        for key, values in query_params.items():
            if key in supported_params:
                filtered_query.append(f"{key}={values[0]}")
        if filtered_query:
            formatted_connection_string += "?" + "&".join(filtered_query)
else:
    formatted_connection_string = None

engine = create_async_engine(
    formatted_connection_string,
    echo=False,  # Set to True for SQL debug logging
    pool_pre_ping=True,
    # Additional asyncpg-specific parameters
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
)

# Create async session
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db_session():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Import models to ensure they're registered with their respective Base classes
from src.models import db_models, chat_models


async def create_tables():
    """Create all tables defined in the models."""
    if not NEONDB_CONNECTION_STRING:
        print("No database connection string provided. Skipping table creation.")
        return

    async with engine.begin() as conn:
        # Create all tables from both existing models and chat models
        await conn.run_sync(MainBase.metadata.create_all)
        await conn.run_sync(ChatBase.metadata.create_all)


async def drop_tables():
    """Drop all tables defined in the models."""
    if not NEONDB_CONNECTION_STRING:
        print("No database connection string provided. Skipping table dropping.")
        return

    async with engine.begin() as conn:
        # Drop all tables from both existing models and chat models
        await conn.run_sync(ChatBase.metadata.drop_all)
        await conn.run_sync(MainBase.metadata.drop_all)