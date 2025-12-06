---
id: 007
title: Switch AI Provider from OpenAI to Gemini
stage: refactor
date: 2025-12-06
surface: agent
model: Gemini
feature: rag
branch: unknown
user: user
command: to ek kam karo openai ki jgh gemini key rakh lo
labels: ["backend", "ai-integration", "gemini", "openai", "refactor"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/core/config.py (modified)
  - backend/.env.example (modified)
  - backend/requirements.txt (modified)
  - backend/src/services/rag_service.py (modified)
  - backend/src/services/translate_service.py (modified)
tests:
  - N/A (requires manual retesting after changes)
---

## Prompt

to ek kam karo openai ki jgh gemini key rakh lo

## Response snapshot

User requested to switch AI provider from OpenAI to Gemini due to OpenAI quota issues. This involves modifying backend configuration, dependencies, and service implementations for RAG and translation.

## Outcome

- ✅ Impact: Initiated task to switch AI provider from OpenAI to Gemini in the backend.
- 🧪 Tests: N/A
- 📁 Files: Plan to modify `backend/src/core/config.py`, `backend/.env.example`, `backend/requirements.txt`, `backend/src/services/rag_service.py`, `backend/src/services/translate_service.py`.
- 🔁 Next prompts: Implement changes for Gemini integration.
- 🧠 Reflection: Successfully understood user's intent to switch AI providers and formulated a comprehensive plan to execute the change, breaking it down into manageable steps.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
