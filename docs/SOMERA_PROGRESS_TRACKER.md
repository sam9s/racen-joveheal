# SOMERA Voice - Progress Tracker

*Last Updated: December 24, 2025*

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

---

## 🚧 In Progress

| Feature | Description | Status |
|---------|-------------|--------|
| "Connecting..." UI | Show connection status with animations | ✅ Complete |
| VAPI Latency Tuning | Target 2-3 second response time (currently 3-5s) | Backend optimized, VAPI dashboard pending |

---

## 📋 Planned Features

### High Priority (Ready to Build)

| Feature | Description | Dependencies |
|---------|-------------|--------------|
| Email Integration | Auto-send booking details to user's email | Shweta's email service info |
| Credit-Based Payment | Usage limits for paid voice feature | Payment integration (Stripe) |

### Credit System Design (Draft)

**Concept:**
- User pays for credits (e.g., $1 = 100 messages)
- Each voice message costs 1 credit
- When credits reach 0, SOMERA prompts to recharge
- Must cover: OpenAI API costs + profit margin

**Pricing Considerations:**
- OpenAI API cost per message (gpt-4o-mini): ~$0.001-0.003
- ElevenLabs TTS cost: varies by character count
- Suggested: 1 cent per message (100 messages/$1) - needs validation

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
| Voice Analytics Dashboard | Call duration, topics, sentiment analysis |
| Appointment Scheduling | Direct calendar integration |
| Progress Tracking for Users | Track user's coaching journey over time |

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

---

## 📝 Notes & Decisions

- **Dec 24, 2024**: Chose pattern-based closure detection over LLM-based for speed. Will add smart detection when we have more transcript data.
- **Credit Pricing**: Need to calculate exact API costs before finalizing. 1 cent/message is placeholder estimate.
- **Email Integration**: Waiting for Shweta (US timezone) to provide email service details.

---

## 🎯 Session Goals

**Current Session:**
1. ~~Add closure patterns~~ ✅
2. Build "Connecting..." UI ⬅️ NOW
3. VAPI latency tuning
4. Plan credit system architecture
