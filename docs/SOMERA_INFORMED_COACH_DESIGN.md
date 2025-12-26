# SOMERA "Informed Coach" Feature Design

*Created: December 26, 2025*
*Status: Awaiting Email Integration*

---

## Overview

This document outlines the design for transforming SOMERA from a "coaching-only" assistant to an "informed coach" who has knowledge of JoveHeal's programs while maintaining her empathetic, non-sales coaching personality.

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

### Example of Ideal Behavior

**User:** "Tell me about the Hustle program"

**New SOMERA:**
> "I sense you're exploring ways to find momentum... The Hustle Program is something Shweta created for professionals feeling stuck in their rhythm. It's about rebuilding drive and reconnecting with your purpose. What's drawing you to explore this right now?"

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
│  Join Intent        │ → "I hear you. If this feels right, you can connect through 
└──────────┬──────────┘    the Discovery Call or contact page."
           │
           ▼
┌─────────────────────┐
│  Provide Links      │ → Share Discovery Call link + Contact page
└──────────┬──────────┘    (NEVER ask for email/phone - privacy guardrail)
           │
           ▼
┌─────────────────────┐
│  Resume Coaching    │ → "Is there anything else you'd like to explore?"
└─────────────────────┘
```

---

## Example Conversation

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | User | "Can you tell me about the Hustle program?" |
| 2 | SOMERA | "I sense you're exploring ways to find momentum... The Hustle Program is something Shweta created for professionals feeling stuck in their rhythm. It's about rebuilding drive and reconnecting with your purpose. What's drawing you to explore this right now?" |
| 3 | User | "I've been feeling burnt out. How can I join this program?" |
| 4 | SOMERA | "I hear you - burnout can feel so heavy, and it's beautiful that you're reaching out for support. If this feels right for you, the best way to connect is through a complimentary Discovery Call with Shweta: https://bit.ly/apply-for-discovery. Is there anything else you'd like to explore about your journey?" |

---

## Critical Guardrails

### Privacy Guardrail (ALREADY IMPLEMENTED)

SOMERA will **NEVER** ask for personal information:
- No collecting emails
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

## Future Enhancement: Email Integration

When Shweta provides email API credentials, we can enhance the flow:

1. User expresses interest in program
2. SOMERA: "Would you like me to send you more details? You can provide your email through our contact page: https://joveheal.com/contact"
3. Kajabi captures the lead
4. Automated email goes out with program details

**Note:** SOMERA never directly collects email - always directs to official JoveHeal channels.

---

## Technical Implementation (When Ready)

### Components to Build

| Component | Description | Status |
|-----------|-------------|--------|
| Intent Detection | Detect program inquiry vs join intent | Not started |
| Program Knowledge | Fetch from Jovee's vector DB | Not started |
| Coaching Templates | Wrap program info in empathetic language | Not started |
| Link Rendering | Show clickable links in voice transcript | Not started |
| Email Integration | Connect to Shweta's email service | Blocked - awaiting credentials |

### Implementation Approach

1. **Extend `somera_engine.py`** with:
   - Intent classifier (program inquiry, join intent)
   - Program brief retriever (from Jovee's vector DB with guardrails)
   - Coaching-style response templates

2. **Add guardrails**:
   - No pricing in responses
   - No hard sell language
   - Always empathetic framing

3. **Update system prompt** to include program knowledge behavior

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Dec 26, 2025 | Wait for email integration before implementing | Avoids broken UX where SOMERA offers to send email but can't |
| Dec 26, 2025 | Privacy guardrails implemented now | Critical safety boundary regardless of feature status |
| Dec 26, 2025 | No direct PII collection | All leads through Kajabi ensures proper data handling |

---

## Dependencies

- [ ] Shweta's email API credentials
- [ ] Shweta's approval of the "informed coach" concept
- [ ] Program brief content curation (key benefits, who it serves)

---

## Next Steps

1. ✅ Document design (this document)
2. ✅ Implement privacy guardrails
3. ⏳ Get Shweta's approval on concept
4. ⏳ Get email API credentials from Shweta
5. ⏳ Build feature when dependencies are met
