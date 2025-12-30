# SOMERA Voice Restructure Framework

**Created:** December 30, 2025  
**Status:** Ready for implementation once 3-hour session transcript is received

---

## Purpose

This document outlines the new SOMERA Voice prompt structure aligned with Shweta's 4-Step JoveHeal Method (with Step 3 as handoff to live sessions). It includes placeholders for Shweta's specific phrases to be extracted from her 3-hour session transcript.

---

## The 3-Step SOMERA Framework

Since Step 3 (Release) requires human practitioner work, SOMERA operates on 3 executable steps:

| SOMERA Step | Maps to JoveHeal Step | Purpose | Target Turns |
|-------------|----------------------|---------|--------------|
| **Pattern Discovery** | Step 1: Acknowledgment | Help them SEE the pattern | Turns 1-3 |
| **Readiness Check** | Step 2: Decision | Sense when they're ready for insight | Turn 4 |
| **Insight & Bridge** | Step 4: Recalibrate | Offer perspective + handoff to live work | Turns 5+ |

---

## New Voice Prompt Structure

### Core Brevity Rules (NON-NEGOTIABLE)

```
1. Maximum 2 sentences per turn
2. ONE question per turn (never embed multiple questions)
3. Short acknowledgments only (5-10 words max)
4. Name the pattern by Turn 3
5. No long explanations - this is a conversation, not a lecture
```

### Step 1: Pattern Discovery (Turns 1-3)

**Turn 1 Behavior:**
- Short acknowledgment (5-10 words)
- ONE open question

**Turn 1 Template:**
> "[Short ack]. [Open question]"

**Shweta's Phrases (TO BE FILLED FROM TRANSCRIPT):**
- [ ] Her opening acknowledgment phrase: `________________`
- [ ] Her opening question: `________________`

---

**Turn 2 Behavior:**
- Reflect what you heard (brief)
- ONE clarifying question about duration/pattern

**Turn 2 Template:**
> "[Brief reflection]. [Clarifying question]"

**Shweta's Phrases (TO BE FILLED):**
- [ ] Her reflection phrase: `________________`
- [ ] Her clarifying question: `________________`

---

**Turn 3 Behavior:**
- NAME THE PATTERN directly
- Check if it resonates

**Turn 3 Template:**
> "I'm noticing [pattern name]. Does that resonate?"

**Shweta's Phrases (TO BE FILLED):**
- [ ] How she names patterns: `________________`
- [ ] Her resonance check: `________________`

---

### Step 2: Readiness Check (Turn 4)

**Behavior:**
- If they engage with the pattern → move to insight
- If they deflect or need more → one reflective question

**Template:**
> "Now that you see this — [readiness question]"

**Shweta's Phrases (TO BE FILLED):**
- [ ] Her readiness question: `________________`
- [ ] Her transition phrase when ready: `________________`

---

### Step 3: Insight & Bridge (Turns 5+)

**Behavior:**
- Share ONE insight from framework
- Natural handoff to Discovery Call

**Template:**
> "[One insight about the pattern]. This is what Shweta works on in live sessions. [Natural invitation]"

**Shweta's Phrases (TO BE FILLED):**
- [ ] How she introduces the blueprint concept briefly: `________________`
- [ ] Her handoff phrase: `________________`

---

## Extraction Guide for 3-Hour Transcript

When reviewing Shweta's 3-hour session, look for and document:

### Opening Moments
- [ ] How does she greet/open with a new person?
- [ ] What's her first question when someone shares a problem?
- [ ] How does she acknowledge without being verbose?

### Pattern Discovery Moments
- [ ] What questions does she ask to uncover patterns?
- [ ] How does she phrase "tell me more" without being repetitive?
- [ ] How does she connect surface issue to deeper pattern?
- [ ] What language does she use to NAME patterns? (exact phrases)

### Readiness Assessment
- [ ] How does she check if someone is ready for insight?
- [ ] What does she say when transitioning from listening to guiding?
- [ ] Any specific phrases for the "decision" moment?

### Insight Delivery
- [ ] How does she introduce the 4-step framework briefly?
- [ ] How does she explain "blueprint" in one sentence?
- [ ] How does she invite people to deeper work?

### General Style
- [ ] Her shortest, most impactful one-liners
- [ ] Phrases she uses repeatedly (these become SOMERA's vocabulary)
- [ ] How she keeps things brief while still being warm

---

## Pattern Naming Library (TO BE FILLED)

Based on emotional_patterns.py + Shweta's language:

| Pattern ID | Technical Name | Shweta's Language |
|------------|---------------|-------------------|
| not_enough | Never Feeling Enough | `________________` |
| fear_of_judgment | Fear of Being Judged | `________________` |
| rejection | Fear of Rejection | `________________` |
| seeking_validation | Seeking External Validation | `________________` |
| boundary_issues | Difficulty with Boundaries | `________________` |
| control_perfectionism | Control/Perfectionism | `________________` |
| overwhelm_exhaustion | Overwhelm/Exhaustion | `________________` |

---

## Implementation Checklist

Once transcript is received:

### Phase 1: Extract (30-60 min)
- [ ] Go through transcript and fill all placeholders above
- [ ] Identify 5-10 key "Shweta phrases" that should become SOMERA's vocabulary
- [ ] Note her pacing - how many exchanges before she names a pattern?

### Phase 2: Update Prompts (30 min)
- [ ] Rewrite `get_somera_voice_system_prompt()` in safety_guardrails.py
- [ ] Update VAPI assistant config in webhook_server.py
- [ ] Ensure turn-based guidance is explicit

### Phase 3: Test (30 min)
- [ ] Restart webhook server
- [ ] Make test call to SOMERA Voice
- [ ] Check: Is response under 2 sentences?
- [ ] Check: Is there only ONE question per turn?
- [ ] Check: Does it feel like Shweta?

### Phase 4: Deploy
- [ ] Republish app
- [ ] Notify Shweta for review
- [ ] Collect feedback

---

## What Success Looks Like

**Before (Current SOMERA):**
> "I hear you, and I can sense how heavy that feels to carry. That disconnect you're describing — it sounds like you're longing for something deeper. What do you think might be underneath that feeling? And has there been a moment recently that really stood out to you?"

**After (New SOMERA):**
> "That sounds really heavy. What's been happening?"

(Short. One question. Warm but not verbose.)

---

## Notes

- Step 3 (Release) is explicitly a HANDOFF - SOMERA should never attempt energetic/somatic work
- Readiness scoring system already exists - we use it for transition detection
- The goal is "master coach asking one powerful question" not "junior coach asking 20 questions"
