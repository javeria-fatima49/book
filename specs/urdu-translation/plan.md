# Implementation Plan: Urdu Translation

**Branch**: `002-urdu-translation` | **Date**: 2025-12-05 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `specs/urdu-translation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The primary requirement is to enable users to translate textbook content to Urdu. The technical approach involves a React-based frontend component (`UrduTranslateButton.tsx`) integrated with a Docusaurus site, and a Python/FastAPI backend. The backend will use an AI translation service and cache translated content.

## Technical Context

**Language/Version**: Python 3.11, Node.js 20.x, TypeScript
**Primary Dependencies**: FastAPI, Docusaurus, React, external AI translation service (e.g., Google Translate API), Redis (for caching).
**Storage**: Redis (for translation cache).
**Testing**: pytest (for Python), Jest/React Testing Library (for TypeScript/React)
**Target Platform**: Web (Docusaurus site)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Average new translation < 5s, cached translation < 1s.
**Constraints**: Securely manage API keys for the translation service.
**Scale/Scope**: Translation feature for a textbook with 13 chapters.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Check**: Pending review of the finalized constitution file (`.specify/memory/constitution.md`). The prompt history indicates that 10 core principles were defined, but the file content is currently a template. This check will be performed once the constitution is available.

## Project Structure

### Documentation (this feature)

```text
specs/urdu-translation/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
backend/
├── src/
│   ├── api/
│   │   ├── rag.py
│   │   └── translate.py
│   ├── core/
│   │   ├── config.py # Already exists, will contain TRANSLATION_API_KEY
│   │   └── redis.py  # New file for Redis client
│   ├── services/
│   │   ├── rag_service.py
│   │   └── translate_service.py
│   └── models/
│       ├── rag_models.py
│       └── translate_models.py
└── tests/
    ├── integration/
    │   ├── test_rag_api.py
    │   └── test_translate_api.py
    └── unit/
        ├── test_rag_service.py
        └── test_translate_service.py

frontend/
├── src/
│   ├── components/
│   │   ├── RAGChatbot.tsx
│   │   └── UrduTranslateButton.tsx
│   ├── pages/
│   │   └── (integrated within Docusaurus pages)
│   └── services/
│       ├── rag_api_client.ts
│       └── translate_api_client.ts
└── tests/
    └── components/
        ├── RAGChatbot.test.tsx
        └── UrduTranslateButton.test.tsx
```

**Structure Decision**: The project will maintain the standard web application structure with separate `frontend` and `backend` directories. The `frontend` will continue to be a Docusaurus project, and the `backend` will remain a FastAPI application. This separation allows for independent development and deployment, and promotes modularity for new features like translation.

## Complexity Tracking

