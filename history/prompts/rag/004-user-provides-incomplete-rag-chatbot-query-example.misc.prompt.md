---
id: 004
title: User Provides Incomplete RAG Chatbot Query Example
stage: misc
date: 2025-12-06
surface: agent
model: Gemini
feature: rag
branch: unknown
user: user
command: when i give this prompt Perception: Robots use sensors (cameras, lidar, microphones) to gather data about their surrou
labels: ["rag", "user-input", "clarification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - null
tests:
  - null
---

## Prompt

when i give this prompt Perception: Robots use sensors (cameras, lidar, microphones) to gather data about their surrou

## Response snapshot

You've provided a partial sentence: "Perception: Robots use sensors (cameras, lidar, microphones) to gather data about their surrou".

If you were to input this into the RAG chatbot (once it's running), here's what should happen:

1.  **Input Validation**: The backend's `/rag/query` endpoint (defined in `backend/src/api/rag.py`) would receive this query. Since `RagQueryRequest` has a `min_length=3` for the query, and your input is longer than 3 characters, it would pass this basic validation.
2.  **Embedding Generation**: The `RagService` would then embed your query using OpenAI's `text-embedding-3-small` model.
3.  **Semantic Search**: This query embedding would be used to perform a semantic search in Qdrant (the `textbook_embeddings` collection).
4.  **Context Retrieval**: Qdrant would return the most relevant content snippets from the textbook (e.g., from Chapter 2: Perception in AI Robotics, which discusses sensors).
5.  **LLM Answer Generation**: An LLM (like OpenAI's GPT-4) would generate an answer based on your query and the retrieved context.
6.  **Response**: The chatbot would display the AI-generated answer and the sources from the textbook that were used.

Given that your input is a partial sentence ("surrou" instead of "surroundings"), the LLM would likely try to make sense of it, but the quality of the answer might be affected by the incompleteness.

To try this yourself, you would need to follow the end-to-end validation steps I provided previously (starting both the backend and frontend servers, and ensuring some textbook content, particularly about "Perception," has been upserted into Qdrant).

## Outcome

- ✅ Impact: User provided example query; agent clarified interpretation and explained expected chatbot behavior based on code review, without live execution.
- 🧪 Tests: N/A
- 📁 Files: N/A
- 🔁 Next prompts: User to clarify intent or proceed with manual validation.
- 🧠 Reflection: Successfully handled ambiguous user input by interpreting it as a RAG query and explaining expected system behavior based on code review, while clearly stating limitations.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
