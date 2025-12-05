---
id: 001
title: Initial project constitution for Physical AI & Humanoid Robotics
stage: constitution
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: User
command: /sp.constitution
labels: ["project-setup", "constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:

---

## Prompt

```text
You are my Expert AI Assistant for the "Physical AI & Humanoid Robotics" Hackathon project.
Your task is to fully generate my project using Claude Code and Spec-Kit Plus.

Follow these rules exactly:

Project metadata:
- Project name: physical-ai-humanoid-robotics
- Repo: create a ready-to-copy folder tree with files and produce a downloadable ZIP or output each file with its full path as headers.
- Node version: 20.x, Python version: 3.11

Requirements:
1) Create the complete Docusaurus (TypeScript) book structure and config.
2) Generate all chapters exactly according to the weekly breakdown (Weeks 1–13).
3) Write full, production-ready textbook content for each chapter (English).
4) Create these frontend components (TypeScript/React, ready for Docusaurus MDX):
   - RAGChatbot.tsx
 tructure
- all source code (frontend + backend)
- all content (13 weeks)
- all configuration & deployment files
- example .env.example and README with run & deploy steps

Constraints:
- Do N  - UrduTranslateButton.tsx
   - PersonalizeButton.tsx
5) Build a FastAPI backend (Python) with these endpoints:
   - /embeddings/upsert → OpenAI embeddings (model: text-embedding-3-small; vector_size=1536) → Qdrant upsert
   - /rag/query → semantic search in Qdrant → LLM answer generation
   - /translate → chapter translation to Urdu
   - /personalize → rewrite chapter based on user profile
6) Integrate Qdrant Cloud and NeonDB (provide connection placeholders and init scripts).
7) Create signup & signin frontend using Better-Auth and persist user profiles in NeonDB.
8) Make everything mobile-friendly and easily deployable (provide Dockerfile(s), GitHub Actions for Docusaurus → GitHub Pages/Vercel, and a deploy guide).
9) Generate all folders, files, and code automatically and ensure TypeScript for frontend and Python for backend.
10) Print all output in ready-to-copy project format (file path header then file contents). Also produce a single zip containing the full project.

Produce:
- folder sOT include long explanations. Do NOT output extraneous commentary.
- If you reach a generation limit, continue automatically until all files are produced.
- Mark any placeholders clearly (e.g., `<OPENAI_KEY>`, `<QDRANT_URL>`, `<GITHUB_USER>`).

Do NOT explain. Just generate the files exactly in project format.
```

## Response snapshot

```text
The project constitution has been updated to version 1.0.0. This is a major version bump as it's the initial definition of the project's core principles and governance.

The following templates require manual follow-up to ensure consistency with the new constitution:
*   `.specify/templates/plan-template.md`
*   `.specify/templates/spec-template.md`
*   `.specify/templates/tasks-template.md`
*   `.specify/templates/commands/*.md`

Suggested commit message:
`docs: amend constitution to v1.0.0 (initial principles and governance)`
```

## Outcome

- ✅ Impact: Constitution established, providing foundational principles for project development.
- 🧪 Tests: N/A
- 📁 Files: .specify/memory/constitution.md updated.
- 🔁 Next prompts: Begin defining feature specifications based on the new constitution.
- 🧠 Reflection: Successfully translated user requirements into a comprehensive project constitution, laying the groundwork for subsequent development phases.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
