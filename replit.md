# JoveHeal Wellness Chatbot

## Overview
The JoveHeal Wellness Chatbot is a RAG-based web chatbot designed for the JoveHeal wellness coaching business. Its primary purpose is to act as a front-line information source for website visitors, answering questions about programs, services, and offerings by leveraging a knowledge base derived from website content and uploaded documents. This MVP aims to enhance user engagement and provide immediate, accurate information about JoveHeal's services.

## User Preferences
I want the agent to focus on high-level features and architectural decisions, avoiding granular implementation specifics unless directly related to a core architectural choice. Please consolidate redundant information and prioritize clarity and conciseness. I prefer a clear, direct communication style. Do not make changes to the existing file structure without explicit approval.

## System Architecture

### UI/UX Decisions
The chatbot, named RACEN (Real-time Advisor for Coaching, Education & Navigation), has a defined personality: warm, empathetic, and guide-like, using plain, human-friendly language. Responses are formatted for readability (short sentences, 2-5 sentences for facts) with empathy prioritized for emotional queries. The frontend is built with Next.js 14, TypeScript, and Tailwind CSS, featuring a branded R.A.C.E.N interface. Streaming responses are implemented using Server-Sent Events (SSE) for a real-time, ChatGPT-like user experience. Clickable links are automatically generated for mentioned JoveHeal programs and pages.

### Technical Implementations
The core system uses a Retrieval Augmented Generation (RAG) approach.
- **SOMERA Coaching Assistant**: A separate empathetic coaching interface at `/somera` that uses Shweta's coaching content from video transcripts. Features streaming SSE responses, purple/pink themed UI, and independent sessions from Jove. Backend endpoints at `/api/somera` and `/api/somera/stream`.
  
  **SOMERA's Core Objective (Updated Dec 2024):**
  SOMERA must behave like a COACH, not a suggestion agent. The goal is to be a compelling first-touch coaching experience that draws users toward Shweta's actual coaching services.
  
  **Coaching Behavior Model:**
  1. NEVER jump straight to solutions - users don't want direct answers
  2. Start with EMPATHY ("I hear you, that sounds difficult...")
  3. Ask TRIAGE QUESTIONS to understand deeper ("Would you like to share more about what's happening?")
  4. LISTEN and probe further before offering any guidance
  5. Help users find THEIR OWN solution (they already know it, just need to realize it)
  6. Use soft, permission-based language for US audience ("I'm sensing you might be feeling...")
  
  **Shweta's JoveHeal 4-Step Framework:**
  | Step | Description |
  |------|-------------|
  | 1. Acknowledgement | Understand what they're going through, patterns, duration |
  | 2. Decision | Help them decide: "Do you want to stay like this or change?" |
  | 3. Release | Various modalities based on person's need (takes most time) |
  | 4. Recalibration | Embodiment of future self without the problem |
  
  **Three Pillars:** Career, Relationship, Wellness
  
  **Key Principle:** "Coaching is all about listening. No one needs a solution - they need to be heard first."
  
  **Cross-Pillar Emotional Pattern System (Dec 2024):**
  SOMERA now understands that emotions don't sit in silos. Key enhancements:
  - `emotional_patterns.py`: Maps career symptoms to childhood root causes (e.g., "can't say no" → "conditional love in childhood")
  - Enhanced retrieval: Searches by emotional pattern FIRST, then filters by pillar
  - Root cause probing: SOMERA can gently explore if patterns show up across career, relationships, and wellness
  - The "Blueprint" concept: Subconscious beliefs, conditioning, and patterns that shape reactions
  
  **Ingested Coaching Content:**
  - Career Healing Course Masterclass (90 chunks, 9 emotional patterns, 10 root causes, all 3 pillars detected)
  - 1-to-1 Educational Concepts (11 chunks) - conceptual frameworks only, no therapeutic scripts
    - Concepts: One Win opening, Blueprint concept, Time patterns, Money energy, Power reclamation, Chocolate analogy, Approval patterns, Standing for yourself, Cross-pillar awareness
  
  **Non-Judgmental Language Guardrails (Dec 2024):**
  SOMERA never makes subjective time judgments like "X years is a long time" or "that's too slow". Output filter automatically corrects these if generated.
  
  **Live Session Referral Boundaries:**
  SOMERA provides coaching support ONLY. These topics require live sessions with Shweta:
  - Deep trauma/regression work
  - Energy healing, chakra work, spiritual practices
  - Guided meditation or altered state work
  - Physical healing claims
  - Ancestral/generational healing
  - "Blueprint" clearing
  
  When these topics arise, SOMERA refers users to book a Discovery Call.
- **Persistent Conversation Memory**: Users can sign in with Google to save conversations to a PostgreSQL database, allowing RACEN to remember past interactions and provide personalized greetings and context-aware responses.
- **Personalized Greetings**: For signed-in users, RACEN offers first-name addressing, welcome-back messages with context from previous conversations, and new user introductions.
- **Smart Conversation Summaries**: LLM-powered summaries of conversations are generated and stored, enabling RACEN to recall specific topics and recommendations for returning users.
- **LLM-Powered Typo Fixer**: Utilizes GPT-4o-mini to correct user typos before RAG retrieval, ensuring accurate search results from the ChromaDB vector store.
- **Knowledge Base**: Supports PDF and text document uploads, and ingests website content. ChromaDB is used for vector storage to enable semantic search.
- **Safety Guardrails**: Includes strict filtering for medical/mental health content, crisis keyword detection with safe redirection, and logging of flagged conversations. SOMERA-specific guardrails include live session referral detection (26+ regex patterns) and non-judgmental time language filters. All guardrail activations are logged to `logs/guardrails/` in JSONL format for monitoring and debugging.
  
  **Documentation:**
  - `docs/somera_production_roadmap.md`: Future production enhancements (NLP intent models, tokenization, varied responses) with decision triggers
  - `docs/somera_guardrails_test_report.md`: Client-ready test report showing guardrails verification
- **Multi-Channel Support**: Integrates with WhatsApp (via Twilio) and Instagram (via Meta Graph API), along with a direct API for custom integrations, maintaining session management and unified logging across channels.
- **Embeddable Widget**: A standalone JavaScript widget (`/widget.js`) that can be embedded on external websites (like Kajabi) with a single script tag. Features a floating chat bubble, streaming responses, and XSS-safe rendering. CORS headers configured for joveheal.com and Kajabi domains.
- **Google OAuth Authentication**: Implemented using NextAuth.js for user sign-in, linking conversations to user accounts in PostgreSQL. Server-side session verification and an internal API key secure communication between Next.js and Flask.
- **Production Reliability**: Includes retry logic on the frontend, a robust startup script (`start_production.sh`) to ensure Flask is healthy before Next.js, a Flask `/health` endpoint, and an auto-rebuild mechanism for the ChromaDB knowledge base on cold starts to ensure data persistence.

### Feature Specifications
- Natural language Q&A with multi-turn context awareness.
- Source attribution for answers.
- User feedback (thumbs up/down with comments).
- Admin Panel for knowledge base management, document upload, conversation logs, analytics, and multi-channel configuration.
- Strict safety policies: no medical/psychological advice, crisis redirection.

### System Design Choices
The architecture separates concerns into a Next.js frontend (port 5000), a Flask backend for webhooks and chat API (port 8080), and a Streamlit admin panel (port 5001). PostgreSQL is the chosen relational database for persistent storage, with SQLAlchemy ORM for data modeling. OpenAI's `gpt-4o-mini` is used as the primary LLM via Replit AI Integrations. ChromaDB handles vector storage. The system is designed to be resilient to Replit's autoscale features through robust startup procedures and knowledge base re-initialization.

## External Dependencies
- **LLM Provider**: OpenAI (via Replit AI Integrations, specifically `gpt-4o-mini`)
- **Vector Database**: ChromaDB
- **Relational Database**: PostgreSQL
- **Frontend Framework**: Next.js (with React, TypeScript, Tailwind CSS)
- **Backend Framework**: Flask
- **Admin Panel Framework**: Streamlit
- **Authentication**: NextAuth.js (with Google OAuth provider)
- **PDF Processing**: PyPDF
- **WhatsApp Integration**: Twilio SDK
- **Instagram Integration**: Meta Graph API
- **Data Analysis**: Pandas (for analytics dashboard)