#  AI Chatbot Backend with RAG Pipeline, JWT Authentication, and Chat History

This project is a backend-only implementation of an intelligent chatbot system built with Django REST Framework. It integrates a Retrieval-Augmented Generation (RAG) pipeline using FAISS and Gemini/OpenAI to deliver context-aware responses. The system supports secure user authentication via JWT, stores chat history, and automates background tasks like cleanup and email verification.

---

##  Project Overview

The chatbot backend is designed for knowledge-driven platforms such as e-commerce support, internal documentation assistants, or customer service bots. It retrieves relevant documents from a vector database, builds contextual prompts, and generates dynamic responses using an AI model. Users can register, log in, chat with the bot, and view their chat history. Background tasks handle housekeeping operations like deleting old sessions and sending verification emails.

---

##  Project Questions Answered

### 1. How did you integrate the RAG pipeline for the chatbot, and what role does document retrieval play in the response generation?

I implemented a RAG (Retrieval-Augmented Generation) pipeline using FAISS for vector-based document retrieval and Gemini/OpenAI for response generation. When a user sends a query, the system retrieves the top-k relevant documents from the vector database, formats them into a structured context, and passes that context to the AI model. This ensures that responses are grounded in the knowledge base and tailored to the user’s question. If no relevant documents are found, the chatbot falls back to a generic AI response.

---

### 2. What database and model structure did you use for storing user and chat history, and why did you choose this approach?

I used SQLite with Django ORM for lightweight and file-based data storage during development. The User model handles authentication, while ChatSession tracks individual conversations and ChatMessage stores each message with a role (user or assistant). This structure supports multi-turn conversations, efficient querying, and future expansion such as analytics or tagging. SQLite is ideal for rapid prototyping and local testing, and the model design ensures clean separation between sessions and messages for maintainability and scalability.

---

### 3. How did you implement user authentication using JWT? What security measures did you take for handling passwords and tokens?

I used `djangorestframework-simplejwt` to implement JWT-based authentication. During registration, passwords are securely hashed using Django’s default PBKDF2 algorithm. Upon login, users receive access and refresh tokens, which are stored client-side and used to authenticate protected endpoints. Sensitive data, such as secret keys and API tokens, is stored in environment variables and never exposed in the codebase. All authentication flows are validated with proper error handling and input sanitization.

---

### 4. How does the chatbot generate responses using the AI model (GPT-3) after retrieving documents?

After retrieving relevant documents using FAISS, the system builds a structured context string that includes document titles, types, categories, and content. This context is passed to the Gemini/OpenAI model along with the user’s query and recent chat history. The AI model uses this combined input to generate a response that is both context-aware and conversational. If no documents are found, the model is instructed to respond with a fallback message or indicate uncertainty.

---

### 5. How did you schedule and implement background tasks for cleaning up old chat history, and how often do these tasks run?

I used APScheduler to schedule background tasks. A daily job runs automatically to delete chat sessions older than 30 days, helping maintain database hygiene and performance. The scheduler is initialized during Django app startup and runs in the background without blocking the main application. I also implemented a task to send verification emails after user signup, ensuring asynchronous handling of non-critical operations.

---

### 6. What testing strategies did you use to ensure the functionality of the chatbot, authentication, and background tasks?

I used a combination of unit and integration testing. Unit tests cover core services such as document retrieval, AI response generation, and authentication logic. Integration tests validate full user flows, including registration, login, chat interaction, and history retrieval. I manually tested all endpoints using Postman and PowerShell to confirm real-world behavior before automating. Background tasks were tested with mock data and scheduled runs to ensure reliability.

---

### 7. What external services (APIs, databases, search engines) did you integrate, and how did you set up and configure them?

I integrated the following external services:
- **Gemini/OpenAI** for AI response generation, configured via API keys stored in `.env`
- **FAISS** for vector-based document retrieval, initialized during app startup
- **PostgreSQL** for persistent storage, configured via Django settings
- **APScheduler** for background task scheduling, loaded via `apps.py`

Each service is modular, environment-driven, and isolated for easier testing and deployment.

---

### 8. How would you expand this chatbot to support more advanced features, such as real-time knowledge base updates or multi-user chat sessions?

To support real-time updates, I would implement a webhook or admin upload interface that triggers document ingestion and FAISS re-indexing. For multi-user chat sessions, I’d extend the `ChatSession` model to support shared sessions and roles, and implement WebSocket support for live messaging. Additional features could include role-based access control, analytics dashboards, multilingual support, and integration with external CRMs or ticketing systems.

---
