# Urdu Translation Quickstart Guide

This guide provides instructions to set up and run the Urdu Translation feature for the Physical AI & Humanoid Robotics textbook.

## 1. Prerequisites

Ensure you have the following installed:

*   **Python 3.11+**
*   **Node.js 20.x+**
*   **npm** (Node Package Manager)
*   **Git**

## 2. Clone the Repository (if not already cloned)

```bash
git clone [YOUR_REPOSITORY_URL]
cd ai_book # or your project root directory
```

## 3. Backend Setup (FastAPI)

Navigate to the `backend` directory and set up the Python environment.

```bash
cd backend
# Assuming venv is already created and activated, and dependencies for RAG are installed
# If not, create venv and install basic dependencies (fastapi, uvicorn, python-dotenv, qdrant-client, openai, psycopg2-binary, fastapi-limiter, redis)
pip install -r requirements.txt # (assuming requirements.txt will be updated/created)
```

### Environment Variables

Ensure your `.env` file in the `backend` directory (based on `.env.example`) has the following:

```
OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY" # Required for mock translation in translate_service
# ... other RAG related keys
REDIS_URL="redis://localhost:6379/0" # Or your Redis instance URL for caching
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
npm install # If not already done for RAG feature
```

### Environment Variables

Ensure your `.env` file in the `frontend` directory has the `BACKEND_API_URL` set:

```
BACKEND_API_URL="http://localhost:8000" # Ensure this matches your backend URL
```

### Run the Frontend

```bash
npm start
```

The Docusaurus website will open in your browser, usually at `http://localhost:3000`.

## 5. Using the Urdu Translation Feature

1.  Once both the backend and frontend are running, navigate to the Docusaurus homepage (e.g., `http://localhost:3000`).
2.  You should see an "Urdu Translate" button (or similar) on the page.
3.  Click the "Translate to Urdu" button.
4.  The main content of the page should be replaced with its Urdu translation.
5.  The button label should change to "Show Original".
6.  Click the "Show Original" button to revert the content back to English.

## 6. Testing Caching (Optional)

To observe caching:
1.  Translate content (step 5).
2.  Observe backend logs for "Cache miss".
3.  Revert to original.
4.  Translate the same content again.
5.  Observe backend logs for "Translation retrieved from cache".
