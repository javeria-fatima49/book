# Book RAG Chatbot System

An integrated Retrieval-Augmented Generation (RAG) chatbot system designed to answer questions about published book content using AI.

## Features

- **RAG Pipeline**: Combines document retrieval with AI generation for accurate, context-aware responses
- **Book Content Management**: Ingest and manage book content with metadata
- **Vector Storage**: Uses Qdrant Cloud for efficient similarity search
- **Database Storage**: Stores book metadata in Neon Serverless Postgres
- **AI Integration**: Powered by Google Gemini API for embeddings and text generation
- **Frontend Interface**: Docusaurus-based interface with chat functionality

## Tech Stack

- **Backend**: FastAPI
- **AI/ML**: Google Gemini API
- **Vector DB**: Qdrant Cloud
- **Relational DB**: Neon Serverless Postgres
- **Frontend**: Docusaurus with React

## Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key
- Qdrant Cloud account
- Neon Serverless Postgres account (optional)

## Setup

### Backend Setup

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```env
   GEMINI_API_KEY="your_gemini_api_key"
   QDRANT_API_KEY="your_qdrant_api_key"
   QDRANT_URL="your_qdrant_url"
   NEONDB_CONNECTION_STRING="your_neon_connection_string"
   REDIS_URL="redis://localhost:6379/0"
   ```

3. Start the backend server:
   ```bash
   cd src
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Usage

### 1. Ingest Book Content

Use the `/api/v1/rag/books/ingest` endpoint to add a book to the system:

```bash
curl -X POST "http://localhost:8000/api/v1/rag/books/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Book Title",
    "author": "Author Name",
    "isbn": "978-1234567890",
    "content": "Full book content goes here..."
  }'
```

### 2. Query the Chatbot

Ask questions about the book content using the `/api/v1/rag/query` endpoint:

```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main theme of the book?",
    "user_id": "optional_user_id"
  }'
```

### 3. Frontend Interface

The chatbot is integrated into the Docusaurus site. Look for the RAG chatbot component on the relevant pages.

## API Endpoints

- `POST /api/v1/rag/query` - Query the RAG system
- `POST /api/v1/rag/embeddings/upsert` - Upsert embeddings to Qdrant
- `POST /api/v1/rag/books/ingest` - Ingest an entire book
- `POST /api/v1/rag/chapters/ingest` - Ingest chapters for a book
- `GET /api/v1/rag/books` - List all books in the system
- `GET /api/v1/rag/health` - Health check endpoint

## Architecture

The system consists of:

1. **Document Ingestion Service**: Processes and stores book content
2. **RAG Service**: Handles embedding, retrieval, and generation
3. **Database Service**: Manages book metadata storage
4. **API Layer**: Exposes functionality via REST endpoints
5. **Frontend Interface**: Provides user interaction

## Testing

Run the test script to verify the pipeline:

```bash
cd backend
python ../test_rag_pipeline.py
```

## Security

- API keys are stored securely in environment variables
- Input validation is performed on all endpoints
- Rate limiting can be configured via the FastAPI setup

## Deployment

For production deployment:

1. Set up SSL certificates
2. Configure a production database
3. Set up a reverse proxy (nginx/Apache)
4. Configure environment-specific variables
5. Set up monitoring and logging

## Troubleshooting

- Ensure all environment variables are set correctly
- Verify Qdrant Cloud connection
- Check that Gemini API is accessible
- Confirm database connection strings are correct
- Check that all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

[Specify your license here]