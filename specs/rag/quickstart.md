# RAG Chatbot Quickstart Guide

This guide provides instructions to set up and run the RAG (Retrieval-Augmented Generation) chatbot for the Physical AI & Humanoid Robotics textbook.

## 1. Prerequisites

Ensure you have the following installed:

*   **Python 3.11+**
*   **Node.js 20.x+**
*   **npm** (Node Package Manager)
*   **Git**

## 2. Clone the Repository

```bash
git clone [YOUR_REPOSITORY_URL]
cd ai_book # or your project root directory
```

## 3. Backend Setup (FastAPI)

Navigate to the `backend` directory and set up the Python environment.

```bash
cd backend
python -m venv venv
./venv/Scripts/activate # On Windows
# source venv/bin/activate # On macOS/Linux
pip install -r requirements.txt # (assuming requirements.txt will be created later)
```

### Environment Variables

Create a `.env` file in the `backend` directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and replace the placeholder values with your actual API keys and connection strings:

```
OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_URL="https://your-qdrant-cluster-url.qdrant.tech"
NEONDB_CONNECTION_STRING="postgresql://user:password@host:port/database"
REDIS_URL="redis://localhost:6379/0" # Or your Redis instance URL
```

### Run the Backend

```bash
./venv/Scripts/activate # On Windows
# source venv/bin/activate # On macOS/Linux
uvicorn src.main:app --reload
```

The backend API will be running at `http://localhost:8000`.

## 4. Frontend Setup (Docusaurus)

Open a new terminal, navigate to the `frontend` directory, and install dependencies.

```bash
cd frontend
npm install
```

### Environment Variables

The frontend reads the `BACKEND_API_URL` from the `.env` file in the `frontend` directory.

Create a `.env` file based on `.env.example` (or manually if not present):

```bash
cp .env.example .env # If you have one, otherwise create it manually
```

Edit the `.env` file and set the `BACKEND_API_URL`:

```
BACKEND_API_URL="http://localhost:8000" # Ensure this matches your backend URL
```

### Run the Frontend

```bash
npm start
```

The Docusaurus website will open in your browser, usually at `http://localhost:3000`.

## 5. Using the RAG Chatbot

1.  Once both the backend and frontend are running, navigate to the RAG Chatbot page on your Docusaurus website (e.g., `http://localhost:3000/rag-chatbot`).
2.  Type your question related to the textbook content into the chat input field.
3.  Press Enter or click the "Send" button.
4.  The chatbot will display an AI-generated answer along with the sources it used from the textbook.

## 6. Upserting Textbook Embeddings

To make the RAG chatbot functional, you need to upsert the textbook content into Qdrant. This can be done by making a POST request to the `/api/v1/embeddings/upsert` endpoint of your backend.

**Example using `curl` (replace with your actual content and metadata):**

```bash
curl -X POST http://localhost:8000/api/v1/embeddings/upsert \
-H "Content-Type: application/json" \
-d 
'{
  "content": "Your textbook chapter content goes here...",
  "metadata": {
    "chapter_title": "Introduction to AI",
    "section_id": "1.1",
    "url": "http://localhost:3000/docs/intro"
  }
}'
```

After upserting, you should be able to query the content via the RAG chatbot.
