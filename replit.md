# JoveHeal Wellness Chatbot

## Overview
A RAG-based web chatbot for JoveHeal wellness coaching business. The chatbot serves as a front-line information bot for website visitors, answering questions about programs, services, and offerings based on a knowledge base derived from website content and uploaded documents.

## Current State
- **Phase**: MVP (Phase 1 - Information Bot)
- **Status**: Active and running
- **Deployment**: Replit with stable URL

## Project Structure

```
├── app.py                  # Main Streamlit application
├── chatbot_engine.py       # Core chatbot logic with RAG
├── knowledge_base.py       # Vector storage and document processing
├── safety_guardrails.py    # Medical/mental health safety filters
├── conversation_logger.py  # Conversation logging system
├── web_scraper.py          # Website content extraction
├── knowledge_base/         # Knowledge base storage
│   └── documents/          # Uploaded documents
├── vector_db/              # ChromaDB vector storage
└── logs/                   # Conversation logs
```

## Key Features

### Chat Interface
- Natural language Q&A about JoveHeal services
- Multi-turn conversation with context awareness
- Source attribution for answers
- Session-based conversation history

### Knowledge Base
- Automatic web scraping of joveheal.com
- PDF document upload and processing
- Text file ingestion
- ChromaDB vector storage for semantic search

### Safety Guardrails
- Strict medical/mental health content filtering
- Crisis keyword detection and safe redirection
- Empathetic responses for high-risk queries
- Logging of flagged conversations

### Admin Panel
- Knowledge base management
- Document upload interface
- Conversation logs and statistics
- Safety flag monitoring

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: OpenAI via Replit AI Integrations (gpt-4o-mini)
- **Vector DB**: ChromaDB
- **Web Scraping**: Trafilatura
- **PDF Processing**: PyPDF

## How to Update Knowledge Base

1. **Website Content**: Go to Admin Panel > Knowledge Base > Click "Refresh Website Content"
2. **PDF Documents**: Go to Admin Panel > Upload Documents > Upload PDF files
3. **Text Files**: Go to Admin Panel > Upload Documents > Upload .txt files

## Safety Guidelines

The chatbot follows strict safety policies:
- No medical, psychological, or therapeutic advice
- No diagnosis or treatment recommendations
- Safe redirection for crisis/distress situations
- Stays within mindset coaching, not therapy

## Future Phases (Planned)
- Phase 2: Booking and scheduling integration
- Phase 3: Multi-channel support (Instagram, WhatsApp)
- Phase 4: User feedback and improvement system
