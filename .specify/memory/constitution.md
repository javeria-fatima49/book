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

---

## 5. Ethics & Safety
- Mandatory chapter: **“Ethics of Physical AI”**  
- No instructions for harmful, unsafe, or illegal robotics.
- create 5 folders and each folder contain 5 chapters 
---

## 6. Performance
- Book must load fast  
- Heavy assets must be **lazy-loaded**

---

## 7. Reusability
- Build **Subagents (Skills)**:  
  - Summary Skill  
  - Quiz Skill  
  - Search Skill  

---

## 8. Deployment
- Deploy to **GitHub Pages** via **GitHub Actions**  
- Backend **local demo** + instructions required
