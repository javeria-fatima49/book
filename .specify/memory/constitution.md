# Project Constitution — "Physical AI & Humanoid Robotics"

## 1. Audience & Tone
- **Target Audience:** Intermediate developers and AI/robotics students
- **Tone:** Technical but easy-to-understand; include diagrams, examples, and quizzes

---

## 2. Tools & Languages
- **Frontend:** TypeScript
- **Backend:** Python (FastAPI)
- **Vector Database:** Qdrant Cloud Free Tier
- **AI Models:** ChatKit / OpenAI Agents / Gemini (Free Keys)
- **Authentication:** Better Auth
- **Documentation:** Docusaurus 3 (MDX)

## 3. Documentation Standards
Every chapter must include:
- **Introduction**
- **Explanation**
- **Code blocks** (MDX + captions)
- **Image placeholder**
- **Conclusion**
- **5 MCQs**

## 4. Structure & File Rules
- **Book content:** `/docs` folder
- **Images:** `/static/img`
- **Backend:** `/backend` folder (FastAPI)
- **Chatbot UI:** Integrated inside `/src/pages/chat`
- **RAG Chatbot:** Implementation must use vector embeddings from Qdrant Cloud
- **User Authentication:** `/auth` endpoints using Better Auth
- **Personalization:** `/features/personalization` with configurable settings
- **Localization:** `/features/translation` with Urdu language support

---

## 5. Core Features Implementation
- **Performance Requirements:** Cache frequently accessed embeddings and implement rate limiting
- **Additional Features:** Support for document upload, content tagging, and conversation history

### 5.2 Subagents & Agent Skills
- **Architecture:** Build modular subagents that can be composed dynamically
- **Skills Required:**
  - **Summary Skill:** Condenses long documents into key points with customizable length
  - **Quiz Skill:** Generates and grades interactive quizzes based on content
  - **Search Skill:** Performs semantic search across document collections
- **Skill Interface:** Define common interface for all skills:
- **Integration:** Skills must be discoverable and composable at runtime

### 5.3 Signup/Signin with Better Auth
- **Implementation:** Use Better Auth library for secure authentication
- **Features Required:**
  - Email/password registration and login
  - OAuth providers (Google, GitHub)
  - Session management
  - Password reset functionality
- **Security:** Implement proper password hashing, CSRF protection, and session validation

### 5.4 Personalization Button
- **Functionality:** Allow users to customize their learning experience
- **Features:**
  - Difficulty level selection (Beginner, Intermediate, Advanced)
  - Preferred AI model choice
  - Theme customization options
  - Learning pace adjustment

### 5.5 Urdu Translation Button
#### Features:
- Translate entire page content to Urdu
- Toggle between original and translated content
- Caching for performance
- Right-to-left layout support
- Error handling and loading states

---

## 6. Ethics & Safety
- Mandatory chapter: **“Ethics of Physical AI”**
- No instructions for harmful, unsafe, or illegal robotics.
- Create 5 folders and each folder contain 5 chapters
- Implement content filtering to prevent generation of unsafe robotics instructions
- Include bias detection mechanisms in AI-generated content

---

## 7. Performance
- Book must load fast
- Heavy assets must be **lazy-loaded**
- Implement progressive image loading for diagrams
- Optimize bundle size through code splitting
- Cache API responses appropriately

---

## 8. Reusability
- Build **Subagents (Skills)**:
  - Summary Skill
  - Quiz Skill
  - Search Skill
- Ensure components are modular and testable
- Implement shared utilities for common operations

---

## 9. Deployment
- Deploy to **GitHub Pages** via **GitHub Actions**
- Backend **local demo** + instructions required
- Include environment configuration for different deployment stages
- Document rollback procedures for failed deployments
