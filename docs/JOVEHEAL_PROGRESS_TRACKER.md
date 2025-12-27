# JoveHeal Progress Tracker

*Last Updated: December 27, 2025*

---

## Product Overview

This tracker covers all three JoveHeal AI products:

| Product | Purpose | Endpoint |
|---------|---------|----------|
| **Jovee (RACEN)** | Business chatbot - website info, programs, pricing | `/` (main site) |
| **SOMERA Text** | Coaching assistant - empathetic text-based coaching | `/somera` |
| **SOMERA Voice** | Coaching assistant - voice-based coaching via VAPI | `/voice` |

---

## Jovee (RACEN) - Business Chatbot

### Completed Features

| Feature | Description | Date |
|---------|-------------|------|
| RAG Knowledge Base | ChromaDB-powered retrieval from JoveHeal website content | Initial build |
| Typo Correction | LLM-powered typo fixer before RAG retrieval | Dec 2024 |
| Google OAuth | User sign-in with personalized greetings | Dec 2024 |
| Conversation Memory | PostgreSQL storage for returning users | Dec 2024 |
| Smart Summaries | LLM-powered conversation summaries for context | Dec 2024 |
| Safety Guardrails | Medical/mental health filtering, crisis detection | Dec 2024 |
| Multi-Channel | WhatsApp (Twilio) + Instagram (Meta Graph API) | Dec 2024 |
| Embeddable Widget | JavaScript widget for Kajabi/external sites | Dec 2024 |
| Streaming Responses | Server-Sent Events for real-time typing effect | Dec 2024 |
| Source Attribution | Shows which content informed the response | Dec 2024 |
| **Rate Limiting** | IP-based protection (10/min, 50/hr, 100/day) | Dec 27, 2024 |
| **IP Logging** | Request logging for monitoring and forensics | Dec 27, 2024 |
| **CAPTCHA Protection** | Math challenge after 20 messages per session | Dec 27, 2024 |

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Enhanced Analytics | User journey tracking, conversion metrics | Medium |
| Multi-language | Hindi, Spanish support | Low |

---

## SOMERA Text - Coaching Assistant

### Completed Features

| Feature | Description | Date |
|---------|-------------|------|
| RAG Knowledge Base | Coaching content from Shweta's methodology | Dec 2024 |
| Readiness Scoring | Dynamic transition from exploration to guidance | Dec 2024 |
| LLM Critic | Language quality filtering for coaching tone | Dec 2024 |
| Safety Guardrails | Non-judgmental language enforcement | Dec 2024 |
| Privacy Guardrails | Never collects personal info (email, phone) | Dec 26, 2024 |
| Empathy-first Design | 4-step coaching framework implementation | Dec 2024 |
| Emotional Pattern System | Maps symptoms to root causes | Dec 2024 |
| Source Citations | "Inspired by" badges for coaching content | Dec 2024 |
| **Markdown Rendering** | Bold text properly rendered in chat | Dec 27, 2024 |
| **Question Throttling** | Limits "Would you be open to..." after 3 turns | Dec 27, 2024 |
| **Early Guidance Trigger** | Solution mode after 2+ help requests (was 7+) | Dec 27, 2024 |
| **Readiness Decay Fix** | "What do you suggest?" maintains guide mode | Dec 27, 2024 |
| **Rate Limiting** | IP-based protection (10/min, 50/hr, 100/day) | Dec 27, 2024 |

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Informed Coach | SOMERA shares program knowledge with coaching warmth | High (awaiting dependencies) |
| Email Integration | Auto-send program details to users | High (awaiting Shweta) |
| Credit-Based Payment | Usage limits for paid feature | High (awaiting Stripe) |

---

## SOMERA Voice - Voice Coaching

### Completed Features

| Feature | Description | Date |
|---------|-------------|------|
| VAPI Integration | Custom LLM mode with Deepgram STT + ElevenLabs TTS | Dec 2024 |
| Shweta's Voice Clone | ElevenLabs voice synthesis | Dec 2024 |
| Voice UI | Professional voice page at `/voice` | Dec 2024 |
| Database Storage | Voice conversations with readiness scores | Dec 2024 |
| Graceful Call Endings | 40+ closure patterns, auto-termination | Dec 24, 2024 |
| Voice-Friendly Booking | Speakable URLs (bit.ly/apply-for-discovery) | Dec 24, 2024 |
| SOMERA Admin Dashboard | Voice analytics with transcripts, latency | Dec 24, 2024 |
| Latency Tracking | Response time per message captured | Dec 24, 2024 |
| "Connecting..." UI | Connection status animations | Dec 26, 2024 |
| "Preparing response..." UI | Yellow bouncing dots during thinking | Dec 26, 2024 |
| Graceful Error Handling | No error on natural call endings | Dec 26, 2024 |
| Password Protection | Demo page with HTTP Basic Auth | Dec 25, 2024 |
| Privacy Guardrails | No PII collection in voice mode | Dec 26, 2024 |

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Informed Coach | Voice-adapted program knowledge sharing | High |
| Credit-Based Payment | Pay-per-use voice coaching | High |
| Multi-language | Hindi voice support | Medium |
| Sentiment Analysis | Emotional pattern detection in voice | Low |

---

## Shared Infrastructure

### Security Features (All Products)

| Feature | Status | Date |
|---------|--------|------|
| Rate Limiting (10/min, 50/hr, 100/day per IP) | Implemented | Dec 27, 2024 |
| Session-based CAPTCHA (after 20 messages) | Implemented | Dec 27, 2024 |
| IP Logging for Forensics | Implemented | Dec 27, 2024 |
| HTTPS Encryption (in-transit) | Active | Always |
| Safety Guardrails (medical, crisis, PII) | Active | Dec 2024 |

### Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | Flask (port 8080) |
| Admin Panel | Streamlit (port 5001) |
| Database | PostgreSQL (Replit Neon) |
| Vector DB | ChromaDB |
| LLM | OpenAI gpt-4o-mini (Replit AI Integrations) |
| Voice STT | Deepgram |
| Voice TTS | ElevenLabs (Shweta's voice) |
| Voice Orchestration | VAPI |

---

## Pending Questions for Shweta

1. Email API details (service provider, credentials)
2. 4-parameter methodology questionnaire for readiness scoring
3. Credit pricing validation (1 cent/message proposed)
4. Approval for "Informed Coach" concept (SOMERA knowing programs)

---

## Next Steps (Priority Order)

1. Get Shweta's approval on "Informed Coach" concept
2. Get email API credentials from Shweta
3. Implement Informed Coach + Email integration together
4. Credit system after pricing validation
5. Production testing of rate limiting

---

## Notes & Decisions Log

| Date | Decision |
|------|----------|
| Dec 27, 2024 | Added rate limiting (10/min, 100/day) and CAPTCHA to all chat endpoints |
| Dec 27, 2024 | Fixed markdown bold rendering in SOMERA Text |
| Dec 27, 2024 | Fixed coaching improvements: early guidance trigger, readiness decay, question throttling |
| Dec 26, 2024 | Privacy guardrails added - no PII collection in any SOMERA mode |
| Dec 26, 2024 | "Informed Coach" designed but NOT implemented (awaiting email integration) |
| Dec 24, 2024 | Pattern-based closure detection chosen over LLM-based for speed |
