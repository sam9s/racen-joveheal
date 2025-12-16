# SOMERA Production Hardening Roadmap

This document outlines future improvements suggested during the MVP development phase. These are production-grade enhancements to implement when SOMERA scales or when current approaches show limitations.

---

## Current Implementation (MVP)

| Component | Approach | Coverage |
|-----------|----------|----------|
| Live Session Referral | 26 regex patterns with word boundaries | ~95% of common phrasings |
| Time Judgment Filter | 17 detection patterns + sentence-scope replacements | Common idioms covered |
| Cross-Pillar Awareness | Emotional pattern mapping + multi-pillar retrieval | Career, Relationship, Wellness |

---

## Future Enhancements

### 1. NLP-Based Intent Classification

**What it is:** Replace regex keyword matching with a machine learning model that understands user *intent* rather than matching exact words.

**Current limitation:**
- Regex: "I want chakra work" triggers referral
- Regex: "I'm curious about working on my energy centers" might NOT trigger (no "chakra" keyword)

**With NLP intent model:**
- Both sentences would be classified as "therapeutic_modality_request" intent
- Model learns semantic meaning, not just keywords

**When to implement:**
- [ ] More than 10% of user queries bypass guardrails despite containing therapeutic requests
- [ ] User feedback indicates SOMERA is attempting therapeutic interventions it shouldn't
- [ ] Database grows beyond 500+ unique conversation patterns
- [ ] You have at least 1,000 labeled examples of queries (referral vs. coaching)

**Implementation options:**
1. **OpenAI Fine-tuning:** Train a classifier on your labeled data
2. **Lightweight model:** Use sentence-transformers for semantic similarity to reference phrases
3. **External service:** Services like Rasa or Dialogflow for intent classification

**Estimated effort:** 2-3 weeks (including data labeling, model training, testing)

---

### 2. Logging & Telemetry for Guardrails

**What it is:** Track every time a guardrail activates - what triggered it, what response was sent, timestamps.

**Current limitation:**
- No visibility into how often guardrails fire
- Difficult to debug user-reported issues
- Can't measure guardrail effectiveness

**When to implement:**
- [ ] More than 50 daily active users
- [ ] Any user report of inappropriate responses
- [ ] Need to demonstrate compliance/safety to stakeholders
- [ ] Want to improve patterns based on real usage data

**What to log:**
```python
{
    "timestamp": "2024-12-16T10:30:00Z",
    "session_id": "abc123",
    "guardrail_type": "live_session_referral",
    "trigger_pattern": "chakra",
    "user_message": "Can you help with chakra healing?",
    "action_taken": "referral_response_sent",
    "response_preview": "I can sense this is something..."
}
```

**Estimated effort:** 1-2 days

---

### 3. Tokenization & Stemming

**What it is:** Use natural language processing to reduce words to root forms automatically.

**Current limitation:**
- Regex must manually enumerate: `heal(ing|er|s)?`
- New variants require pattern updates

**With stemming:**
- "healing", "healer", "healers", "healed" all reduce to "heal"
- One pattern catches all variants

**When to implement:**
- [ ] Maintaining regex patterns becomes burdensome (50+ patterns)
- [ ] Users consistently use word forms not covered by patterns
- [ ] Adding new therapeutic modalities frequently

**Libraries to consider:**
- NLTK (Python): `PorterStemmer` or `WordNetLemmatizer`
- spaCy (Python): Full NLP pipeline with lemmatization

**Estimated effort:** 3-5 days (including testing edge cases)

---

### 4. Varied Referral Responses

**What it is:** Instead of one canned response for all live session topics, use multiple context-aware templates.

**Current limitation:**
- Same response for chakra AND regression feels repetitive
- Users may feel dismissed if response seems too generic

**Improved approach:**
```python
REFERRAL_TEMPLATES = {
    "energy_work": "The kind of energy work you're describing is something Shweta works with deeply...",
    "regression": "Exploring those past patterns at that level is powerful work that Shweta guides in her sessions...",
    "inner_child": "That kind of deep inner child work is something Shweta holds space for in her 1-to-1 sessions...",
    "default": "What you're describing would really benefit from Shweta's deeper work..."
}
```

**When to implement:**
- [ ] User feedback mentions responses feel "robotic" or "canned"
- [ ] Improving conversational flow becomes a priority
- [ ] A/B testing shows varied responses improve conversion to Discovery Calls

**Estimated effort:** 1-2 days

---

## Decision Triggers Summary

| Signal | Action |
|--------|--------|
| >10% queries bypassing guardrails | Implement NLP intent classification |
| >50 daily users OR compliance needs | Add logging/telemetry |
| >50 regex patterns to maintain | Add tokenization/stemming |
| User feedback: "feels robotic" | Add varied responses |
| Database >500 unique patterns | Consider ML-based approach |
| Performance issues (response latency) | Optimize retrieval pipeline |

---

## Quick Wins (Implement Anytime)

1. **Basic logging** - Low effort, high debugging value
2. **Add patterns as gaps discovered** - Iterate based on real conversations
3. **Varied responses** - Improves UX with minimal complexity

---

## Notes

- The current MVP implementation is production-ready for initial launch
- Primary defense is always the system prompt (instructs SOMERA on behavior)
- Regex patterns are a secondary safety net
- All enhancements should be driven by real user data, not hypothetical edge cases

*Last updated: December 2024*
