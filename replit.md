# JoveHeal Wellness Chatbot

## Overview
A RAG-based web chatbot for JoveHeal wellness coaching business. The chatbot serves as a front-line information bot for website visitors, answering questions about programs, services, and offerings based on a knowledge base derived from website content and uploaded documents.

## Current State
- **Phase**: MVP with Multi-Channel Support
- **Status**: Active and running
- **Deployment**: Replit with stable URL

## Project Structure

```
├── app.py                  # Main Streamlit application
├── chatbot_engine.py       # Core chatbot logic with RAG
├── knowledge_base.py       # Vector storage and document processing
├── safety_guardrails.py    # Medical/mental health safety filters
├── conversation_logger.py  # Conversation logging to PostgreSQL
├── database.py             # SQLAlchemy models and DB connection
├── channel_handlers.py     # Multi-channel message handlers
├── webhook_server.py       # Flask webhook API server
├── embed_widget.py         # Embeddable chat widget
├── web_scraper.py          # Website content extraction
├── knowledge_base/         # Knowledge base storage
│   └── documents/          # Uploaded documents
├── vector_db/              # ChromaDB vector storage
└── logs/                   # Conversation logs (legacy)
```

## Key Features

### Chat Interface
- Natural language Q&A about JoveHeal services
- Multi-turn conversation with context awareness
- Source attribution for answers
- Session-based conversation history
- User feedback with thumbs up/down and optional comments

### Knowledge Base
- PDF document upload and processing
- Text file ingestion with validation
- **Website content ingested** (7 pages, 60+ chunks):
  - Homepage - business overview, Shaveta's story
  - Services - full list including Relationship Healing, Career Healing, Balance Mastery, etc.
  - About - Shaveta's background, mission, qualifications
  - Balance Mastery - 3-month premium 1:1 coaching program details
  - Inner Mastery Lounge - membership community and course library
  - Elevate 360 - 5-month group healing program
  - Testimonials - client success stories
- ChromaDB vector storage for semantic search
- Content validation (rejects binary/malformed content)

### Safety Guardrails
- Strict medical/mental health content filtering
- Crisis keyword detection and safe redirection
- Empathetic responses for high-risk queries
- Logging of flagged conversations

### Admin Panel
- Knowledge base management
- Document upload interface
- Conversation logs and statistics
- Analytics dashboard with daily trends
- Feedback summary with comments
- Embed widget code generation
- Multi-channel configuration status

### Multi-Channel Support
- **WhatsApp** via Twilio - receive and respond to WhatsApp messages
- **Instagram** via Meta Graph API - receive and respond to DMs
- **Direct API** - REST endpoint for custom integrations
- Session management across channels
- Unified conversation logging

### Database Integration
- PostgreSQL for persistent conversation storage
- SQLAlchemy ORM with models: ChatSession, Conversation, ResponseFeedback, AnalyticsDaily
- Automatic schema initialization
- Migration utility for legacy file-based logs

## Tech Stack
- **Frontend**: Streamlit
- **Backend API**: Flask (for webhooks)
- **LLM**: OpenAI via Replit AI Integrations (gpt-4o-mini)
- **Vector DB**: ChromaDB
- **Database**: PostgreSQL
- **PDF Processing**: PyPDF
- **WhatsApp**: Twilio SDK
- **Analytics**: Pandas

## Workflows
1. **Start application** - Main Streamlit app on port 5000
2. **Webhook Server** - Flask API on port 8080 for external integrations

## How to Update Knowledge Base

1. **PDF Documents**: Go to Admin Panel > Upload Documents > Upload PDF files
2. **Text Files**: Go to Admin Panel > Upload Documents > Upload .txt files

Files are validated before ingestion to ensure readable text content.

## Multi-Channel Setup

### WhatsApp (Twilio)
Required secrets:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`

Security: WhatsApp webhooks use Twilio signature validation. For custom deployments, set `WEBHOOK_BASE_URL` to your trusted base URL.

### Instagram (Meta Graph API)
Required secrets:
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_PAGE_ID`
- `INSTAGRAM_VERIFY_TOKEN`

### Session Storage Note
Channel sessions are stored in-process memory. For multi-worker deployments, implement Redis or database-backed session storage.

See Admin Panel > Channels tab for detailed setup instructions.

## API Endpoints

- `POST /api/chat` - Send a message and get a response
- `POST /api/chat/reset` - Reset conversation session
- `GET /api/channels/status` - Check channel configuration status
- `POST /webhook/whatsapp` - Twilio WhatsApp webhook
- `GET/POST /webhook/instagram` - Meta Instagram webhook

## Safety Guidelines

The chatbot follows strict safety policies:
- No medical, psychological, or therapeutic advice
- No diagnosis or treatment recommendations
- Safe redirection for crisis/distress situations
- Stays within mindset coaching, not therapy

## Future Phases (Planned)
- Phase 3: Booking and scheduling integration
