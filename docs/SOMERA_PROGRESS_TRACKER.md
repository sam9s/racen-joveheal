# SOMERA Voice - Progress Tracker

*Last Updated: December 26, 2025*

---

## ✅ Completed Features

| Feature | Description | Date |
|---------|-------------|------|
| VAPI Integration | Custom LLM mode with Deepgram STT + ElevenLabs TTS (Shweta's voice) | Dec 2024 |
| Voice UI | Professional voice page at `/voice` with branded design | Dec 2024 |
| Readiness Scoring | Dynamic transition from exploration → guidance mode (20%/35% thresholds) | Dec 2024 |
| Database Storage | Voice conversations & messages stored with readiness scores | Dec 2024 |
| Graceful Call Endings | 40+ closure patterns, VAPI auto-termination on strong closures | Dec 24, 2024 |
| Voice-Friendly Booking | Speakable URLs + clickable transcript links (bit.ly/apply-for-discovery) | Dec 24, 2024 |
| Backup Scripts | Code backup to GitHub, database backup working | Dec 2024 |
| SOMERA Admin Dashboard | Voice analytics dashboard with transcripts, latency metrics, readiness journey | Dec 24, 2024 |
| Latency Tracking | Capture & display response time per message in database | Dec 24, 2024 |
| "Connecting..." UI | Show connection status with animations during call setup | Dec 26, 2024 |
| "Preparing response..." UI | Yellow bouncing dots during SOMERA's thinking time | Dec 26, 2024 |
| Graceful Error Handling | No error message shown when calls end naturally | Dec 26, 2024 |
| Password Protection | Demo page protected with HTTP Basic Auth | Dec 25, 2024 |
| **Privacy Guardrails** | SOMERA (Voice & Text) never collects personal info (email, phone, etc.) | Dec 26, 2024 |

---

## 🚧 In Progress

| Feature | Description | Status |
|---------|-------------|--------|
| Informed Coach Design | Design doc for SOMERA knowing programs with coaching warmth | ✅ Design complete, awaiting dependencies |

---

## 📋 Planned Features

### High Priority (Ready to Build When Dependencies Met)

| Feature | Description | Dependencies |
|---------|-------------|--------------|
| **Informed Coach** | SOMERA shares program knowledge with empathetic delivery | Email integration + Shweta approval |
| **Email Integration** | Auto-send program details/booking links to users | Shweta's email service info (Kajabi) |
| **Credit-Based Payment** | Usage limits for paid voice feature | Payment integration (Stripe) |

### Informed Coach Feature (Designed - Awaiting Implementation)

See `docs/SOMERA_INFORMED_COACH_DESIGN.md` for full design.

**Summary:**
- SOMERA becomes an "informed coach" who knows JoveHeal programs
- Delivers program info with coaching warmth, not sales pitch
- Pattern: Empathy → Brief context → Coaching follow-up
- Directs to Discovery Call/Contact page (never collects PII directly)
- Awaiting: Email integration + Shweta's approval

### Credit System Design (Draft)

**Concept:**
- User pays for credits (e.g., $1 = 100 messages)
- Each voice message costs 1 credit
- When credits reach 0, SOMERA prompts to recharge
- Must cover: OpenAI API costs + ElevenLabs + profit margin

**Pricing Considerations:**
- OpenAI API cost per message (gpt-4o-mini): ~$0.001-0.003
- ElevenLabs TTS cost: varies by character count
- VAPI costs: orchestration fees
- Suggested: 1 cent per message (100 messages/$1) - needs validation with Shweta

**Database Requirements:**
- `user_credits` table: user_id, credit_balance, last_updated
- `credit_transactions` table: transaction history, amounts, timestamps

---

### Medium Priority (Needs More Info)

| Feature | Description | Waiting On |
|---------|-------------|------------|
| Readiness Scoring Optimization | Fine-tune with Shweta's 4-parameter methodology | Questionnaire answers |
| Smart Closure Detection | LLM-based intent detection for flexible farewells | More voice transcripts |
| Voice Transcript Analysis | Analyze real calls to improve coaching | Data collection ongoing |

---

### Future Enhancements

| Feature | Description |
|---------|-------------|
| Multi-language Support | Support for Hindi, Spanish, etc. |
| Appointment Scheduling | Direct calendar integration |
| Progress Tracking for Users | Track user's coaching journey over time |
| Sentiment Analysis | Detect emotional patterns in voice calls |

---

## 🔧 Technical Notes

### Architecture
- **VAPI**: Orchestration layer (Custom LLM mode)
- **Deepgram**: Speech-to-text
- **ElevenLabs**: Text-to-speech (Shweta's cloned voice)
- **Base URL**: `https://jove-heal-chatbot--sam9s.replit.app/api/vapi`
- **Voice URL**: `somera.sam9scloud.in/voice`

### VAPI Configuration
- Public Key: `135fdcab-d4e9-4729-ac09-a905d8793170`
- Assistant ID: `c09f6a3b-35d5-4e23-bd67-36299a4f44dd`

### Readiness Thresholds
- Transition mode: 20%
- Guidance mode: 35%

### Knowledge Base Architecture (Current)
- **Jovee (RACEN)**: Uses ChromaDB `jovee_collection` - JoveHeal website content, programs, courses
- **SOMERA Voice**: Uses VAPI webhook → `somera_engine.py` with separate coaching knowledge
- **Gap**: SOMERA doesn't query Jovee's program database (by design, pending Informed Coach feature)

### Safety Guardrails
- Crisis keyword detection with professional referrals
- Mental health/medical content redirects
- Non-judgmental language enforcement
- Live session referral boundaries
- **Privacy guardrails** - No PII collection (implemented Dec 26, 2024)

---

## 📝 Notes & Decisions

- **Dec 26, 2024**: Privacy guardrails added to both SOMERA Voice and SOMERA Text. Neither will ever ask for personal information.
- **Dec 26, 2024**: "Informed Coach" feature designed but NOT implemented. Waiting for email integration to avoid broken UX.
- **Dec 26, 2024**: Fixed "Preparing response..." UI to show during SOMERA's thinking time.
- **Dec 26, 2024**: Improved error handling - normal call terminations no longer show error messages.
- **Dec 24, 2024**: Chose pattern-based closure detection over LLM-based for speed.
- **Credit Pricing**: Need to calculate exact API costs before finalizing. 1 cent/message is placeholder estimate.
- **Email Integration**: Waiting for Shweta (US timezone) to provide email service details.

---

## 📌 Pending Questions for Shweta

See `docs/questions_for_shweta.md` for full list:
1. Email API details (service provider, credentials)
2. 4-parameter methodology questionnaire for readiness scoring
3. Credit pricing validation (1 cent/message proposed)
4. **NEW:** Approval for "Informed Coach" concept (SOMERA knowing programs)

---

## 🎯 Next Steps (Priority Order)

1. ⏳ Get Shweta's approval on "Informed Coach" concept
2. ⏳ Get email API credentials from Shweta
3. ⏳ Implement Informed Coach + Email integration together
4. ⏳ Credit system after pricing validation
