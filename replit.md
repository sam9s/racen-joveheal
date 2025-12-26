# JoveHeal Wellness Chatbot

## Overview
The JoveHeal Wellness Chatbot, named RACEN (Real-time Advisor for Coaching, Education & Navigation), is a RAG-based web chatbot for the JoveHeal wellness coaching business. Its primary purpose is to serve as a front-line information source for website visitors, answering questions about programs and services using a knowledge base derived from website content and uploaded documents. A key component is the SOMERA Coaching Assistant, an empathetic AI coach designed to provide a compelling first-touch coaching experience aligned with Shweta's 4-step framework and emotional pattern recognition. This project aims to enhance user engagement, provide immediate, accurate information, and guide users towards JoveHeal's coaching services.

## User Preferences
I want the agent to focus on high-level features and architectural decisions, avoiding granular implementation specifics unless directly related to a core architectural choice. Please consolidate redundant information and prioritize clarity and conciseness. I prefer a clear, direct communication style. Do not make changes to the existing file structure without explicit approval.

**Re-publishing Reminder**: Always proactively remind me to re-publish the app after making any code changes (backend or frontend). Code changes only go live after publishing.

## System Architecture

### Assistant Architecture (IMPORTANT)

The system has three distinct assistants sharing common infrastructure:

| Assistant | Purpose | Engine | Knowledge Base |
|-----------|---------|--------|----------------|
| **Jovee/RACEN** | Business assistant - website info, programs, pricing | `chatbot_engine.py` | ChromaDB (website/programs) |
| **SOMERA Text** | Coaching assistant - empathy, 4-step framework | `somera_engine.py` | ChromaDB (coaching content) |
| **SOMERA Voice** | Same as SOMERA Text, voice interface via VAPI | `somera_engine.py` | ChromaDB (coaching content) |

**SOMERA Voice and SOMERA Text are the same coaching assistant** - they share:
- The same `generate_somera_response()` function
- The same RAG/knowledge base queries
- The same guardrails and safety filters
- The same readiness scoring system

**Key Delivery Differences (Same Logic, Different Output):**

| Aspect | SOMERA Text | SOMERA Voice |
|--------|-------------|--------------|
| Links | Display clickable URLs | NEVER speak URLs - offer to email instead |
| Citations | Show "Inspired by" badges | Log for transcripts only |
| Discovery Call | Share link directly | "Would you like me to email you the link?" |

See `docs/SOMERA_INFORMED_COACH_DESIGN.md` for full design details.

**Shared Privacy Guardrails (All Three Assistants):**
All assistants use `filter_response_for_safety()` from `safety_guardrails.py` which includes:
- PII detection/blocking (email, phone, address requests)
- Medical/mental health safety redirects
- Crisis keyword detection
- Judgmental language correction

Lead capture happens only through official Kajabi channels (Discovery Call link, Contact page).

### UI/UX Decisions
RACEN presents a warm, empathetic, and guide-like personality, using plain language. Responses are formatted for readability, and emotional queries are handled with empathy. The frontend is built with Next.js 14, TypeScript, and Tailwind CSS, featuring a branded R.A.C.E.N interface. Streaming responses are implemented via Server-Sent Events (SSE) for a real-time user experience. Clickable links are automatically generated for mentioned JoveHeal programs. SOMERA has a distinct purple/pink themed UI.

### Technical Implementations
The system utilizes a Retrieval Augmented Generation (RAG) approach.
- **SOMERA Coaching Assistant**: An empathetic coaching interface at `/somera` using Shweta's coaching content. It functions as a coach, not an advice giver, focusing on empathy, triage questions, active listening, and guiding users to their own solutions, adhering to Shweta's 4-Step Framework and the "Three Pillars" (Career, Relationship, Wellness). It incorporates an "Emotional Pattern System" to map symptoms to root causes and an LLM Critic for dynamic language quality filtering, ensuring a coaching tone and adherence to guardrails. A **Readiness Scoring System** (`readiness_scoring.py`) uses weighted heuristics to detect when users are ready to transition from exploration to guidance, based on breakthrough insights, confusion signals, emotional exhaustion, and conversation depth.
- **Persistent Conversation Memory**: Google-signed-in users can save conversations to a PostgreSQL database for personalized greetings and context.
- **Personalized Greetings**: For signed-in users, RACEN offers first-name addressing, welcome-back messages, and new user introductions.
- **Smart Conversation Summaries**: LLM-powered summaries enable recall of past topics and recommendations.
- **LLM-Powered Typo Fixer**: Uses GPT-4o-mini to correct user input before RAG retrieval.
- **Knowledge Base**: Supports PDF/text document uploads and website content ingestion, using ChromaDB for vector storage.
- **Safety Guardrails**: Includes filtering for medical/mental health content, crisis keyword detection with redirection, and logging. SOMERA has specific guardrails for live session referrals and non-judgmental language.
- **Multi-Channel Support**: Integrates with WhatsApp (Twilio) and Instagram (Meta Graph API) with unified session management and logging.
- **Embeddable Widget**: A standalone JavaScript widget (`/widget.js`) for external websites (e.g., Kajabi) with XSS-safe rendering.
- **Google OAuth Authentication**: Uses NextAuth.js for user sign-in and links conversations to user accounts in PostgreSQL.
- **Production Reliability**: Includes frontend retry logic, a robust `start_production.sh` script, a Flask `/health` endpoint, and auto-rebuild of the ChromaDB knowledge base on cold starts.
- **Admin Dashboard Transcription**: A feature within the admin dashboard to transcribe audio/video files using OpenAI Whisper API, saving transcripts to `transcripts/`.
- **SOMERA Admin Dashboard** (`somera_admin.py`): A dedicated analytics dashboard for SOMERA Voice and text coaching sessions. Features include:
  - **Voice Analytics**: Total calls, messages, average latency, booking conversion rate
  - **Latency Trends**: Charts showing response time over the past 30 days
  - **Readiness Distribution**: Visualization of explore/transition/guide score distribution
  - **Transcripts**: Full call history with user messages showing readiness scores and assistant messages showing latency
  - **Coaching Insights**: Conversion funnel, peak readiness analysis, and threshold metrics
  - Run with: `streamlit run somera_admin.py --server.port 5001`

### Feature Specifications
- Natural language Q&A with multi-turn context.
- Source attribution for answers.
- User feedback (thumbs up/down).
- Admin Panel for knowledge base management, document upload, conversation logs, analytics, and multi-channel configuration.
- Strict safety policies: no medical/psychological advice, crisis redirection.

### System Design Choices
The architecture separates concerns into a Next.js frontend (port 5000), a Flask backend for webhooks and chat API (port 8080), and a Streamlit admin panel (port 5001). PostgreSQL is the relational database with SQLAlchemy ORM. OpenAI's `gpt-4o-mini` is the primary LLM via Replit AI Integrations. ChromaDB is used for vector storage. The system is designed for resilience within Replit's autoscale environment.

## External Dependencies
- **LLM Provider**: OpenAI (`gpt-4o-mini` via Replit AI Integrations)
- **Vector Database**: ChromaDB
- **Relational Database**: PostgreSQL
- **Frontend Framework**: Next.js (React, TypeScript, Tailwind CSS)
- **Backend Framework**: Flask
- **Admin Panel Framework**: Streamlit
- **Authentication**: NextAuth.js (Google OAuth)
- **PDF Processing**: PyPDF
- **WhatsApp Integration**: Twilio SDK
- **Instagram Integration**: Meta Graph API
- **Data Analysis**: Pandas (for analytics dashboard)
- **Transcription**: OpenAI Whisper API