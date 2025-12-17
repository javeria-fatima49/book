import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.api.rag import router as rag_router
import logging
from contextlib import asynccontextmanager
from src.core.database import create_tables

load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize database on startup."""
    logger.info("Initializing database tables...")
    try:
        await create_tables()
        logger.info("Database tables initialized successfully!")
    except Exception as e:
        logger.warning(f"Database initialization failed (this may be expected if database is not configured): {e}")
        # Continue startup even if database fails - this allows the app to run with just Qdrant
        pass
    yield  # Application runs during this period
    # Any cleanup code would go here if needed

app = FastAPI(title="AI Book RAG Chatbot API", lifespan=lifespan)

# Add CORS middleware - this is essential for frontend communication
# For development with React frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # React development server
        "http://localhost:8000",
        "http://localhost:8001",  # Backend itself
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        # Add your production domain here in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose the authorization header so frontend can read it
    expose_headers=["Access-Control-Allow-Origin"]
)

from src.api.user_profile import router as user_profile_router
from src.api.auth import router as auth_router

# Include the RAG router
app.include_router(rag_router, prefix="/api/v1/rag", tags=["rag"])

# Include the auth router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

# Include the user profile router
app.include_router(user_profile_router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Book RAG Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Book RAG Chatbot API"}

# Server startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)