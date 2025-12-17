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

### 5.1 RAG Chatbot
The RAG (Retrieval-Augmented Generation) chatbot must be implemented with:

#### Full Implementation Instructions:
1. **Setup Environment Variables:**
   ```bash
   # .env.local
   QDRANT_URL=https://your-cluster.qdrant.tech:6333
   QDRANT_API_KEY=your_qdrant_api_key
   OPENAI_API_KEY=your_openai_api_key
   NEXT_PUBLIC_AI_PROVIDER=openai # or gemini or chatkit
   ```

2. **Database Schema:**
   Create collection in Qdrant Cloud with vectors:
   ```json
   {
     "collection_name": "book_content",
     "vectors_config": {
       "size": 1536,
       "distance": "Cosine"
     },
     "payload_schema": {
       "chapter_id": "keyword",
       "content_text": "text",
       "page_number": "integer",
       "book_section": "keyword"
     }
   }
   ```

3. **Install Dependencies:**
   ```bash
   npm install @qdrant/js-client-rest @langchain/core @langchain/openai
   ```

#### Vector Storage Setup with Qdrant:
```typescript
// lib/qdrant.ts
import { QdrantClient } from '@qdrant/js-client-rest';
import { OpenAIEmbeddings } from "@langchain/openai";

const client = new QdrantClient({
  url: process.env.QDRANT_URL,
  apiKey: process.env.QDRANT_API_KEY,
});

export const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
});

export const setupCollection = async () => {
  try {
    await client.createCollection("book_content", {
      vectors: {
        size: 1536,
        distance: "Cosine",
      },
    });
  } catch (error) {
    console.log("Collection already exists");
  }
};

export const storeDocument = async (text: string, metadata: any) => {
  const embedding = await embeddings.embedQuery(text);

  await client.upsert("book_content", {
    points: [{
      id: Math.floor(Math.random() * 100000),
      vector: embedding,
      payload: {
        content: text,
        ...metadata
      }
    }]
  });
};
```

#### Query Processing:
```typescript
// lib/search.ts
import { client, embeddings } from './qdrant';

export const searchDocuments = async (query: string, limit: number = 5) => {
  const queryEmbedding = await embeddings.embedQuery(query);

  const results = await client.search("book_content", {
    vector: queryEmbedding,
    limit: limit,
    with_payload: true,
  });

  return results.map(result => ({
    content: result.payload?.content as string,
    score: result.score,
    metadata: result.payload
  }));
};
```

#### Response Generation:
```typescript
// lib/ai.ts
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

export const generateResponse = async (query: string, context: string[]) => {
  const llm = new ChatOpenAI({
    openAIApiKey: process.env.OPENAI_API_KEY,
    modelName: "gpt-3.5-turbo",
  });

  const template = `
    You are an expert AI assistant for Physical AI & Humanoid Robotics education.
    Use the following context to answer the user's question accurately and comprehensively.

    Context: {context}

    User Question: {question}

    Provide a detailed, technical answer that intermediate developers and AI/robotics students can understand.
    Use diagrams, examples, and include relevant code snippets where appropriate.
  `;

  const prompt = PromptTemplate.fromTemplate(template);
  const chain = prompt.pipe(llm).pipe(new StringOutputParser());

  return await chain.invoke({
    context: context.join("\n\n"),
    question: query
  });
};
```

#### Complete Frontend Component:
```typescript
// src/components/RAGChat.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types/chat';

const RAGChatBot = ({ userId }: { userId?: string }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call RAG API
      const response = await fetch('/api/rag-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input,
          userId: userId || 'anonymous'
        }),
      });

      const data = await response.json();
      const botMessage: Message = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-t-lg">
        <h2 className="text-xl font-bold">AI Assistant for Physical AI & Robotics</h2>
      </div>

      <div className="flex-grow bg-white dark:bg-gray-900 p-4 overflow-y-auto max-h-[60vh]">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 p-3 rounded-lg ${
              message.role === 'user'
                ? 'bg-blue-100 dark:bg-blue-900 ml-10 text-right'
                : 'bg-gray-100 dark:bg-gray-800 mr-10'
            }`}
          >
            <div className="font-semibold capitalize mb-1">
              {message.role}:
            </div>
            <div dangerouslySetInnerHTML={{ __html: message.content }} />
          </div>
        ))}

        {isLoading && (
          <div className="mb-4 p-3 rounded-lg bg-gray-100 dark:bg-gray-800 mr-10">
            <div className="font-semibold">Assistant:</div>
            <div className="animate-pulse">Thinking...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t bg-white dark:bg-gray-900 rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Physical AI, Robotics, or related topics..."
            className="flex-grow px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default RAGChatBot;
```

#### Backend API Endpoint:
```typescript
// pages/api/rag-chat.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { searchDocuments } from '../../lib/search';
import { generateResponse } from '../../lib/ai';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { query, userId } = req.body;

  try {
    // Retrieve relevant documents
    const searchResults = await searchDocuments(query);
    const contexts = searchResults.map(r => r.content);

    // Generate AI response
    const response = await generateResponse(query, contexts);

    // Log interaction for analytics
    console.log(`RAG Chat interaction by ${userId}: ${query}`);

    res.status(200).json({ response });
  } catch (error) {
    console.error('RAG Chat error:', error);
    res.status(500).json({
      error: 'Failed to process your request',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
```

- **Performance Requirements:** Cache frequently accessed embeddings and implement rate limiting
- **Additional Features:** Support for document upload, content tagging, and conversation history

### 5.2 Subagents & Agent Skills
- **Architecture:** Build modular subagents that can be composed dynamically
- **Skills Required:**
  - **Summary Skill:** Condenses long documents into key points with customizable length
  - **Quiz Skill:** Generates and grades interactive quizzes based on content
  - **Search Skill:** Performs semantic search across document collections
- **Skill Interface:** Define common interface for all skills:
  ```python
  # Example in backend/subagents/base.py
  class BaseSkill:
      async def execute(self, input_data: dict) -> dict:
          raise NotImplementedError
  ```
- **Integration:** Skills must be discoverable and composable at runtime

### 5.3 Signup/Signin with Better Auth
- **Implementation:** Use Better Auth library for secure authentication
- **Features Required:**
  - Email/password registration and login
  - OAuth providers (Google, GitHub)
  - Session management
  - Password reset functionality
- **Code Example:**
  ```typescript
  // Example in /pages/api/auth/[...nextauth].ts
  import { BetterAuth } from "better-auth";
  import { nextJs } from "better-auth/next-js";

  const auth = BetterAuth({
    database: {
      // Database configuration
    },
    socialProviders: {
      google: {
        clientId: process.env.GOOGLE_CLIENT_ID!,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      }
    }
  });

  export const { signIn, signOut, authHandler } = nextJs(auth);
  ```
- **Security:** Implement proper password hashing, CSRF protection, and session validation

### 5.4 Personalization Button
- **Functionality:** Allow users to customize their learning experience
- **Features:**
  - Difficulty level selection (Beginner, Intermediate, Advanced)
  - Preferred AI model choice
  - Theme customization options
  - Learning pace adjustment
- **Implementation:**
  ```typescript
  // Example in /components/PersonalizationPanel.tsx
  interface PersonalizationSettings {
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
    preferredModel: 'openai' | 'gemini' | 'chatkit';
    theme: 'light' | 'dark' | 'auto';
    learningPace: 'slow' | 'medium' | 'fast';
  }

  const PersonalizationButton = () => {
    // Implementation for the personalization panel
  };
  ```

### 5.5 Urdu Translation Button
#### Complete Implementation for Content Translation:
The Urdu translation functionality has been implemented with the following components:

#### 1. Frontend Component:
```typescript
// src/components/UrduTranslateButton.tsx
import React, { useState, useRef, useEffect } from 'react';
import { translateContent } from '../services/translate_api_client';

interface UrduTranslateButtonProps {
  backendApiUrl: string;
}

const UrduTranslateButton: React.FC<UrduTranslateButtonProps> = ({ backendApiUrl }) => {
  const [isTranslated, setIsTranslated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const originalContentRef = useRef<string | null>(null);
  const mainContentElementId = 'docusaurus-main-content';

  // Store original content on first render
  useEffect(() => {
    const mainContentElement = document.getElementById(mainContentElementId);
    if (mainContentElement && originalContentRef.current === null) {
      originalContentRef.current = mainContentElement.innerHTML;
    }
  }, []);

  const handleTranslate = async () => {
    setLoading(true);
    setError(null);
    const mainContentElement = document.getElementById(mainContentElementId);

    if (!mainContentElement) {
      setError('Main content element not found.');
      setLoading(false);
      return;
    }

    try {
      if (!isTranslated) {
        // Translate to Urdu
        const contentToTranslate = originalContentRef.current || mainContentElement.innerHTML;
        const targetLanguage = "ur";

        const response = await translateContent(
          { content: contentToTranslate, target_language: targetLanguage },
          backendApiUrl
        );
        mainContentElement.innerHTML = response.translated_content;
        setIsTranslated(true);
        // Set RTL direction for Urdu
        mainContentElement.dir = 'rtl';
      } else {
        // Revert to original content
        if (originalContentRef.current) {
          mainContentElement.innerHTML = originalContentRef.current;
        }
        setIsTranslated(false);
        // Reset direction to LTR
        mainContentElement.dir = 'ltr';
      }
    } catch (err: any) {
      console.error('Error translating content:', err);
      setError(err.message || 'Failed to translate content.');
      if (isTranslated && originalContentRef.current) {
        mainContentElement.innerHTML = originalContentRef.current;
        setIsTranslated(false);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleTranslate}
      disabled={loading}
      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
    >
      {loading ? 'Translating...' : (isTranslated ? 'Show Original' : 'Translate to Urdu')}
      {error && <span style={{ color: 'red', marginLeft: '10px' }}>{error}</span>}
    </button>
  );
};

export default UrduTranslateButton;
```

#### 2. Frontend API Client:
```typescript
// src/services/translate_api_client.ts
export interface TranslateRequest {
  content: string;
  target_language: string;
  source_language?: string;
}

export interface TranslateResponse {
  translated_content: string;
}

export const translateContent = async (
  request: TranslateRequest,
  backendApiUrl: string
): Promise<TranslateResponse> => {
  const response = await fetch(`${backendApiUrl}/api/v1/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to translate content.');
  }

  return response.json();
};
```

#### 3. Backend Translation Service:
```python
# backend/src/services/translate_service.py
from src.models.translate_models import TranslateRequest, TranslateResponse
from src.core.redis import get_redis_client
from src.core.config import GEMINI_API_KEY
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.redis_client = get_redis_client()
        genai.configure(api_key=GEMINI_API_KEY)
        self.gemini_client = genai
        self.llm_model = "gemini-pro"
        self.llm = genai.GenerativeModel(self.llm_model)

    async def _call_ai_translation_service(self, text: str, target_language: str) -> str:
        logger.info(f"Calling AI translation service for text: '{text[:50]}...' to {target_language}")
        try:
            response = await self.llm.generate_content([
                f"Translate the following English text to {target_language}:",
                text
            ])
            translated_text = response.candidates[0].content.parts[0].text.strip()
            logger.info(f"AI translation successful for text: '{text[:50]}...'")
            return translated_text
        except Exception as e:
            logger.error(f"Error calling AI translation service: {e}")
            raise

    async def translate_content(self, request: TranslateRequest) -> TranslateResponse:
        cache_key = f"translation:{request.source_language}-{request.target_language}:{hash(request.content)}"

        # Try to retrieve from cache
        cached_translation = await self.redis_client.get(cache_key)
        if cached_translation:
            logger.info(f"Translation retrieved from cache for key: {cache_key}")
            return TranslateResponse(translated_content=cached_translation)

        logger.info(f"Cache miss for translation key: {cache_key}. Calling AI translation service.")

        # If not in cache, call AI translation service
        translated_text = await self._call_ai_translation_service(
            request.content, request.target_language
        )

        # Store in cache
        await self.redis_client.set(cache_key, translated_text, ex=3600)  # Cache for 1 hour
        logger.info(f"Translation stored in cache for key: {cache_key}")

        return TranslateResponse(translated_content=translated_text)
```

#### 4. Backend Translation API:
```python
# backend/src/api/translate.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.translate_models import TranslateRequest, TranslateResponse
from src.services.translate_service import TranslationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_translation_service() -> TranslationService:
    return TranslationService()

@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(
    request: TranslateRequest,
    translation_service: TranslationService = Depends(get_translation_service),
):
    logger.info(
        f"Received translation request for content (first 50 chars): '{request.content[:50]}...'"
        f" to language: {request.target_language}"
    )
    try:
        response = await translation_service.translate_content(request)
        logger.info("Translation successful.")
        return response
    except ValueError as e:
        logger.error(f"Bad request for translation: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Internal server error during translation.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
```

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
