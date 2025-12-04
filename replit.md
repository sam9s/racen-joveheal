# JoveHeal Wellness Chatbot

## Overview
A RAG-based web chatbot for JoveHeal wellness coaching business. The chatbot serves as a front-line information bot for website visitors, answering questions about programs, services, and offerings based on a knowledge base derived from website content and uploaded documents.

## Current State
- **Phase**: MVP with Multi-Channel Support
- **Status**: Active and running
- **Deployment**: Replit with stable URL + Custom Domain

## Live URLs
- **Custom Domain**: https://jove.sam9scloud.in (via Caddy reverse proxy on Hostinger VPS)
- **Replit URL**: https://jove-heal-chatbot--sam9s.replit.app
- **Admin Panel**: Run `streamlit run app.py --server.port 5001` for Streamlit admin access

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

### RACEN Persona
RACEN (Real-time Advisor for Coaching, Education & Navigation) has a defined personality:
- **Tone**: Warm, empathetic, guide-like (not salesy)
- **Language**: Plain, human-friendly (no therapy-speak or jargon)
- **Formatting**: Short sentences, 2-5 sentences for facts, empathy-first for emotional queries
- **Boundaries**: Honest about being AI when asked; no medical/therapy advice
- **Behavior**: Offers next steps, admits uncertainty openly, refers to humans when needed

### Chat Interface
- Natural language Q&A about JoveHeal services
- Multi-turn conversation with context awareness
- Context-aware search for follow-up questions (e.g., "tell me more about that program")
- Source attribution for answers
- Session-based conversation history
- User feedback with thumbs up/down and optional comments

### Persistent Conversation Memory (Dec 2025)
When users sign in with Google:
- All conversations are saved to PostgreSQL database
- Sessions are linked to user accounts
- Returning users load their last 50 messages from previous sessions
- RACEN remembers what you discussed and can continue the conversation
- In-memory buffer keeps last 100 messages (50 exchanges) per session

### Personalized Greetings (Dec 2025)
RACEN provides personalized experiences for signed-in users:
- **First-name addressing**: "Hi Sammy!" instead of generic greetings
- **Welcome-back messages**: Returning users get "It's great to see you back!" with context about their last conversation topics
- **New user introductions**: First-time users get a friendly intro explaining who RACEN is
- **Session ID timing fix**: Frontend waits for auth check before generating session ID, ensuring logged-in users aren't treated as guests

### Smart Conversation Summaries (Dec 2025)
RACEN generates and stores structured conversation summaries for returning users:
- **LLM-powered summarization**: After 2+ exchanges, generates summary with emotional_themes, recommended_programs, last_topics
- **Database storage**: Summaries stored in `conversation_summaries` table per user
- **Contextual welcome-back**: Returning users get specific references like "I remember you mentioned feeling disconnected from society and stressed about your career - I suggested Beyond the Hustle for you"
- **Implementation**: `generate_conversation_summary()` in chatbot_engine.py, stored via `upsert_conversation_summary()` in database.py

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
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS (R.A.C.E.N branded)
- **Backend API**: Flask (webhooks and chat API on port 8080)
- **Admin Panel**: Streamlit (separate access on port 5001)
- **LLM**: OpenAI via Replit AI Integrations (gpt-4o-mini)
- **Vector DB**: ChromaDB
- **Database**: PostgreSQL
- **PDF Processing**: PyPDF
- **WhatsApp**: Twilio SDK
- **Analytics**: Pandas

## Workflows
1. **Frontend** - Next.js app on port 5000
2. **Webhook Server** - Flask API on port 8080 for chat and external integrations

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

## Google OAuth Authentication (Dec 2025)

### Overview
Web users can sign in with their Google account to enable persistent conversation history across visits.

### Implementation
- **NextAuth.js** with Google provider for OAuth 2.0 authentication
- **User accounts stored** in PostgreSQL `user_accounts` table
- **Multi-channel identity** support (Google for web, platform IDs for WhatsApp/Instagram)

### Required Secrets
- `GOOGLE_CLIENT_ID` - OAuth client ID from Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - OAuth client secret
- `NEXTAUTH_SECRET` - Secret for session encryption (auto-generated)
- `NEXTAUTH_URL` - Base URL for NextAuth (https://jove.sam9scloud.in for production)

### Security Features
- Server-side session verification via `getServerSession()`
- Internal API key (`INTERNAL_API_KEY`) for trusted Next.js to Flask communication
- Flask backend only trusts user identity from verified Next.js requests
- Direct API calls without valid internal key are treated as anonymous

### User Flow
1. User clicks "Sign In" button in header
2. Redirects to Google OAuth consent screen
3. After authorization, returns to app with session
4. Session persists across page refreshes
5. User's conversation history is tied to their Google email

### Publishing OAuth App
The Google OAuth app must be published to "Production" mode in Google Cloud Console for all users to sign in (not just test users).

To publish:
1. Go to Google Cloud Console > APIs & Credentials > OAuth consent screen
2. Review app information and branding
3. Click "Publish App" to move from Testing to Production
4. May require Google verification for sensitive scopes

### Files
- `src/app/api/auth/[...nextauth]/route.ts` - NextAuth configuration
- `src/components/Header.tsx` - Sign In/Sign Out UI
- `src/components/SessionProvider.tsx` - Client session provider
- `database.py` - UserAccount model and helper functions

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

## Clickable Program Links (Implemented Dec 2025)

RACEN now includes clickable links when mentioning any JoveHeal program:
- Balance Mastery → https://joveheal.com/balance-mastery/
- Inner Mastery Lounge → https://joveheal.com/inner-mastery-lounge/
- Elevate 360 → https://joveheal.com/elevate-360/
- Relationship Healing → https://joveheal.com/relationship-healing/
- Career Healing → https://joveheal.com/career-healing/
- Beyond the Hustle → https://joveheal.com/beyond-the-hustle/
- Inner Reset → https://joveheal.com/inner-reset/
- Shed & Shine → https://joveheal.com/shed-and-shine/
- Services → https://joveheal.com/services/
- About → https://joveheal.com/about/
- Testimonials → https://joveheal.com/testimonials/
- Contact → https://joveheal.com/contact/

**Implementation:**
- URL mapping: `JOVEHEAL_PROGRAM_URLS` in safety_guardrails.py
- Prompt injection: Detailed persona includes link instructions and examples
- UI rendering: `renderMarkdownLinks()` in ChatMessage.tsx converts markdown links to clickable `<a>` tags

## RACEN Persona Configuration

- **Toggle**: `RACEN_PERSONA_MODE` environment variable
  - `detailed` (default): Priority-ladder persona with examples - warm, empathetic responses
  - `simple`: Original concise persona - fallback option
- **Location**: `safety_guardrails.py` → `get_racen_persona()` function

## Production Reliability (RCA Fix - Dec 2025)

### Issue
After 24 hours of no traffic, Replit's autoscale feature suspended the app. On wake-up, Next.js started serving traffic before Flask was ready, causing chat errors.

### Fixes Applied
1. **Retry Logic**: Frontend API route now retries 3 times with 1-second delays if Flask isn't ready
2. **Startup Script**: `start_production.sh` ensures Flask is healthy before Next.js starts
3. **Health Endpoint**: Flask has `/health` endpoint for monitoring
4. **Auto-Rebuild Knowledge Base**: ChromaDB vector database auto-rebuilds on cold starts if empty

### Knowledge Base Cold Start Fix (Dec 2025)
Replit autoscale deployments don't persist local files after cold starts. The `vector_db/` folder with ChromaDB data would be lost.

**Solution**: On Flask startup, `init_knowledge_base_on_startup()` checks if the vector DB is empty. If so, it:
1. Loads 73 chunks from pre-saved documents in `knowledge_base/documents/`
2. Scrapes the JoveHeal website for ~34 additional chunks
3. Total: ~107 chunks ready for RAG queries

This ensures production always has the same knowledge as development, even after cold starts.

### Deployment Configuration
To apply the startup script fix, update the deployment run command in Deployments settings:

**Current (problematic):**
```
npx next start -p 5000 -H 0.0.0.0 & python webhook_server.py
```

**Recommended (robust):**
```
bash start_production.sh
```

### Monitoring Recommendation
Consider adding an external uptime monitor (e.g., UptimeRobot, Pingdom) to hit `/health` endpoint every 5 minutes during business hours. This keeps the app warm and alerts on failures.

## Future Phases (Planned)
- Phase 3: Booking and scheduling integration
- Phase 4: Client VPS deployment (after v1 finalization)
  - Move PostgreSQL and ChromaDB to client's own VPS
  - Eliminates container timeout/ephemeral storage issues
  - Full data ownership for client
  - Docker Compose packaging for easy deployment
