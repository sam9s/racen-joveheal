# SOMERA "Informed Coach" Feature Design

*Created: December 26, 2025*
*Updated: December 26, 2025*
*Status: Awaiting Email Integration*

---

## Overview

This document outlines the design for transforming SOMERA from a "coaching-only" assistant to an "informed coach" who has knowledge of JoveHeal's programs while maintaining her empathetic, non-sales coaching personality.

**Important:** This document covers both SOMERA Text and SOMERA Voice, which share the same coaching logic but have different delivery mechanisms.

---

## SOMERA Text vs SOMERA Voice: Key Distinctions

| Aspect | SOMERA Text | SOMERA Voice |
|--------|-------------|--------------|
| **Interface** | Chat UI at /somera | Voice via VAPI at /voice |
| **Link Sharing** | Display clickable URLs inline | NEVER speak URLs - offer to email instead |
| **Formatting** | Rich text, line breaks, emojis | Conversational, no visual formatting |
| **Citations** | Show "Inspired by" badges | Log for transcripts only, never vocalize |
| **Discovery Call** | Share link: https://bit.ly/apply-for-discovery | "Would you like me to email you the link?" |
| **Contact Info** | Share link: https://joveheal.com/contact | Describe how to find it or offer email |

**Core Principle:** Same coaching logic, different delivery. Voice must never make the user write down URLs.

---

## The Problem

Currently, SOMERA responds to program questions like this:

**User:** "Can you tell me about the Hustle program?"

**Current SOMERA:**
> "I hear you, and it's understandable to want to learn more about programs that can support your journey. While I'm not equipped with specific details about the Hustle program, I can certainly listen to your experiences and feelings..."

This makes SOMERA sound like an outsider rather than part of Shweta's team.

---

## The Vision: "Coach Who Knows"

A real assistant coach working for Shweta would naturally know about the programs. SOMERA should deliver program information with coaching warmth, not as a sales pitch.

### Response Pattern

1. **Empathetic acknowledgment** - validates the underlying feeling
2. **Brief program context** - just the essence, not a sales pitch
3. **Coaching follow-up** - turns it back into exploration

---

## Conversation Flow: Complete State Machine

```
┌─────────────────────┐
│  Baseline Coaching  │ ← Normal empathetic coaching
└──────────┬──────────┘
           │ "Tell me about Hustle program"
           ▼
┌─────────────────────┐
│  Program Inquiry    │ → Empathetic response + program context + coaching follow-up
└──────────┬──────────┘
           │ "How do I join?" / "How do I contact Shweta?"
           ▼
┌─────────────────────┐
│  Join Intent        │ → Modality-specific response (see below)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Resume Coaching    │ → "Is there anything else you'd like to explore?"
└─────────────────────┘
```

### Join Intent - Modality-Specific Behavior

**SOMERA Text:**
> Share Discovery Call link directly in the response

**SOMERA Voice:**
> Offer to email the link, then continue coaching

---

## Example Conversations

### SOMERA Text Example

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | User | "Can you tell me about the Hustle program?" |
| 2 | SOMERA Text | "I sense you're exploring ways to find momentum... The Hustle Program is something Shweta created for professionals feeling stuck in their rhythm. It's about rebuilding drive and reconnecting with your purpose. What's drawing you to explore this right now?" |
| 3 | User | "I've been feeling burnt out. How can I join this program?" |
| 4 | SOMERA Text | "I hear you - burnout can feel so heavy, and it's beautiful that you're reaching out for support. If this feels right for you, the best way to connect is through a complimentary Discovery Call with Shweta: https://bit.ly/apply-for-discovery. Is there anything else you'd like to explore about your journey?" |

### SOMERA Voice Example

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | User | "Can you tell me about the Hustle program?" |
| 2 | SOMERA Voice | "I sense you're exploring ways to find momentum... The Hustle Program is something Shweta created for professionals feeling stuck in their rhythm. It's about rebuilding drive and reconnecting with your purpose. What's drawing you to explore this right now?" |
| 3 | User | "I've been feeling burnt out. How can I join this program?" |
| 4 | SOMERA Voice | "I hear you - burnout can feel so heavy, and it's beautiful that you're reaching out for support. The best way to connect is through a complimentary Discovery Call with Shweta. Would you like me to email you the link to book that call?" |
| 5 | User | "Yes please" |
| 6 | SOMERA Voice | *[Email integration sends link]* "Done! I've sent that to your email. Now, while you wait for that - is there anything else you'd like to explore about your journey?" |

**Key Difference:** SOMERA Voice never speaks URLs. It offers to email them instead.

---

## Critical Guardrails

### Privacy Guardrail (ALREADY IMPLEMENTED)

Both SOMERA Text and SOMERA Voice will **NEVER** ask for personal information:
- No collecting emails directly in conversation
- No collecting phone numbers
- No collecting addresses
- No collecting any PII

All lead capture happens through:
- Discovery Call booking (Kajabi): https://bit.ly/apply-for-discovery
- Contact page: https://joveheal.com/contact

### Coaching Guardrails

SOMERA remains a coach, not a salesperson:
- ✅ Share program context with empathy
- ✅ Connect programs to user's expressed needs
- ✅ Guide to Discovery Call when appropriate
- ❌ No hard selling
- ❌ No pricing details
- ❌ No pushy calls-to-action

---

## Email Integration Design (For SOMERA Voice)

### The Flow

1. User asks about joining a program via SOMERA Voice
2. SOMERA Voice: "Would you like me to email you the link to book a Discovery Call?"
3. User says "Yes"
4. System retrieves user's verified email (from prior authentication or Kajabi integration)
5. Email sent with Discovery Call link
6. SOMERA Voice: "Done! I've sent that to your email. Is there anything else you'd like to explore?"
7. Coaching continues

### Email Scenarios

| Scenario | SOMERA Voice Behavior |
|----------|----------------------|
| User authenticated, email known | Send email automatically, confirm "Sent!" |
| User not authenticated | "You can book directly at joveheal.com - just look for Discovery Call on the homepage" |
| Email service unavailable | "I'm having trouble with email right now. You can visit joveheal.com and look for Discovery Call to book directly" |

### Guardrail: No Direct Email Collection

Even in voice, SOMERA never asks "What's your email?"

Instead:
- Use pre-authenticated email if available
- Or direct to website/contact page

---

## Technical Implementation (When Ready)

### Modality Parameter

Add `modality` parameter throughout the response pipeline:

```python
def generate_somera_response(
    user_message: str,
    conversation_history: list,
    modality: str = "text"  # "text" or "voice"
) -> dict:
```

### Post-Processing by Modality

| Processing Step | Text | Voice |
|-----------------|------|-------|
| Insert hyperlinks | Yes | No - replace with email offer |
| "Inspired by" citations | Show inline | Log only, don't vocalize |
| Formatting (bullets, line breaks) | Preserve | Convert to natural speech |

### Components to Build

| Component | Description | Status |
|-----------|-------------|--------|
| Modality Parameter | Pass "text" or "voice" through pipeline | Not started |
| Intent Detection | Detect program inquiry vs join intent | Not started |
| Program Knowledge | Fetch from Jovee's vector DB | Not started |
| Voice Link Handler | Replace URLs with email offer for voice | Not started |
| Email Integration | Connect to Shweta's email service | Blocked - awaiting credentials |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Dec 26, 2025 | Wait for email integration before implementing | Avoids broken UX where SOMERA offers to send email but can't |
| Dec 26, 2025 | Privacy guardrails implemented now | Critical safety boundary regardless of feature status |
| Dec 26, 2025 | No direct PII collection | All leads through Kajabi ensures proper data handling |
| Dec 26, 2025 | Voice never speaks URLs | Speaking links ruins voice UX - offer email instead |
| Dec 26, 2025 | Add modality parameter to pipeline | Enables Text vs Voice behavioral differences |

---

## Dependencies

- [ ] Shweta's email API credentials
- [ ] Shweta's approval of the "informed coach" concept
- [ ] Program brief content curation (key benefits, who it serves)
- [ ] Modality parameter implementation in somera_engine.py

---

## Next Steps

1. ✅ Document design (this document)
2. ✅ Implement privacy guardrails
3. ✅ Clarify Text vs Voice distinctions
4. ⏳ Get Shweta's approval on concept
5. ⏳ Get email API credentials from Shweta
6. ⏳ Implement modality parameter in pipeline
7. ⏳ Build feature when dependencies are met

---

## Future Enhancements (Documented, Not Yet Implemented)

### Enhancement 1: Visual Link Display in Voice Transcript

**Status:** Documented, awaiting email integration

**Concept:** When SOMERA Voice mentions a link (Discovery Call, program page), display the clickable link in the transcript UI without speaking it.

**User Experience:**
```
SOMERA: "The best way to connect is through a Discovery Call with Shweta. 
        Would you like me to email you the link?"

        📎 Book Discovery Call →
```

**Technical Approach (Option B - Backend Metadata):**
- Backend returns structured response: `{spoken_text: "...", display_links: [{text, url}]}`
- Frontend receives via websocket/polling alongside VAPI transcript
- Frontend renders spoken text + clickable links below

**Dependencies:**
- Email integration (so "Would you like me to email..." actually works)
- Additional websocket channel for metadata delivery

---

### Enhancement 2: ElevenLabs Voice Speed Control

**Status:** Awaiting documentation from user

**Concept:** Control SOMERA Voice speed and other parameters via ElevenLabs API.

**Implementation:** Configure in VAPI assistant settings or direct API calls.

---

### Enhancement 3: Jovee Auto-Navigation (Future Feature)

**Status:** Concept documented, implementation deferred

**Concept:** Jovee (the business assistant widget on joveheal.com) can offer to navigate users directly to program pages.

**User Experience:**
```
User: "Tell me about the Hustle program"
Jovee: "The Hustle Program helps professionals rebuild their drive. 
       Would you like me to take you to that page?"
User: "Yes"
*Browser navigates to joveheal.com/hustle*
```

**Technical Approach:**
1. Intent detection: Detect "take me there" / "yes" after navigation offer
2. URL mapping: Map program names to website URLs
3. Widget communication: Use `postMessage` API to send navigation command from widget to parent page
4. Parent handler: Kajabi site receives message and navigates

**Code Pattern:**
```javascript
// Widget sends navigation command
window.parent.postMessage({type: 'navigate', url: 'https://joveheal.com/hustle'}, '*');

// Parent page handler
window.addEventListener('message', (e) => {
  if (e.data.type === 'navigate') window.location.href = e.data.url;
});
```

**This applies to Jovee only** - not SOMERA Text or SOMERA Voice, since those are coaching sessions where navigation would interrupt the flow.
