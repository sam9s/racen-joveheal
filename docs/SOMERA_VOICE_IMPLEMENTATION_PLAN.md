# SOMERA Voice Implementation Plan

## Comprehensive Strategy for 90% Shweta Fidelity

**Created:** December 31, 2025  
**Status:** Draft - Pending Review by Shweta  
**Git Branch:** `somera-voice-improvements`  
**Fallback:** Can revert to `main` branch or checkpoint `d333478` if issues arise

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Architecture](#current-architecture)
3. [The Problem We're Solving](#the-problem-were-solving)
4. [CRITICAL: SOMERA Text Protection Strategy](#critical-somera-text-protection-strategy)
5. [Proposed Solution Architecture](#proposed-solution-architecture)
6. [Implementation Phases](#implementation-phases)
7. [Technical Specifications](#technical-specifications)
8. [Risk Assessment](#risk-assessment)
9. [Success Criteria](#success-criteria)
10. [Rollback Plan](#rollback-plan)
11. [Questions for Shweta](#questions-for-shweta)

---

## Executive Summary

### Goal
Transform SOMERA Voice from a generic coaching AI into a 90% accurate representation of Shweta's coaching style and methodology.

### Key Insight
We are NOT hardcoding Shweta's phrases. Instead, we are:
1. Teaching the AI Shweta's **behavioral patterns** (how she structures conversations)
2. Using **few-shot examples** from transcripts (not scripts, but tone references)
3. Enforcing **hard constraints** (brevity, single question per turn)
4. Leveraging **existing RAG** for actual coaching solutions

### Core Principle
```
RAG Knowledge Base = WHAT Shweta would teach (the solutions)
Style Layer (new)  = HOW Shweta would deliver it (the methodology)
```

### Critical Architecture Constraint
**SOMERA Voice and SOMERA Text share the same backend function:** `generate_somera_response()` in `somera_engine.py`. 

This means:
- ALL changes to this function affect BOTH modes
- We MUST use conditional logic to isolate Voice-specific behavior
- We MUST test Text mode before and after every change
- Failure to do this will break the existing Text product

See [SOMERA Text Protection Strategy](#critical-somera-text-protection-strategy) for detailed safeguards.

---

## Current Architecture

### How SOMERA Works Today

```
┌─────────────────────────────────────────────────────────────────┐
│                     CURRENT SOMERA FLOW                         │
└─────────────────────────────────────────────────────────────────┘

User Message
     │
     ├──► identify_emotional_patterns()
     │    └── Detects: not_enough, prove_worth, fear_of_judgment, etc.
     │
     ├──► identify_pillars()
     │    └── Detects: career, relationship, wellness
     │
     ├──► search_coaching_content_enhanced() ◄──── RAG RETRIEVAL
     │    └── Queries ChromaDB with pattern + pillar hints
     │    └── Returns Shweta's coaching content from transcripts
     │
     ├──► calculate_readiness_score()
     │    └── Returns: explore (<35%), transition (35-70%), guide (>70%)
     │
     ├──► get_somera_system_prompt()
     │    └── Returns static behavioral instructions
     │
     ├──► Assemble Prompt
     │    └── System prompt + RAG content + user message + history
     │
     ├──► LLM Call (gpt-4o-mini)
     │    └── Generates response
     │
     └──► Post-processing
          └── apply_llm_critic() + filter_response_for_safety()
```

### What's Working Well
| Component | File | Status |
|-----------|------|--------|
| Pattern detection | `emotional_patterns.py` | ✅ Working |
| Pillar detection | `emotional_patterns.py` | ✅ Working |
| RAG retrieval | `knowledge_base.py` | ✅ Working |
| Readiness scoring | `readiness_scoring.py` | ✅ Working |
| Turn counting | `somera_engine.py` | ✅ Exists |
| Safety filters | `safety_guardrails.py` | ✅ Working |

### What's Not Working
| Issue | Impact |
|-------|--------|
| Generic system prompt | LLM doesn't know Shweta's style |
| No turn-aware behavior | Same approach for Turn 1 vs Turn 5 |
| No readiness-aware prompting | Same tone for explore vs guide mode |
| No brevity enforcement | Responses too long for voice |
| Repetitive acknowledgments | "I hear you" over and over |

---

## The Problem We're Solving

### Current Behavior (Generic)
```
User: "I feel exhausted all the time, like nothing I do is ever enough."

SOMERA (current): "I hear you, and I can sense how heavy that feels. That 
feeling of exhaustion and never being enough is something many people 
struggle with. It sounds like you're carrying a lot. Have you noticed 
when this feeling started? And what areas of your life does it affect 
the most? I'm here to listen and support you."
```

**Problems:**
- Too long (5 sentences)
- Multiple questions (2)
- Generic coaching-speak
- No pattern naming
- No Shweta-specific methodology

### Desired Behavior (Shweta-style)
```
User: "I feel exhausted all the time, like nothing I do is ever enough."

SOMERA (target): "That sounds really heavy. How long have you been 
carrying this?"
```

**Characteristics:**
- Brief (2 sentences)
- Single question
- Body-aware ("carrying")
- No lecturing
- Shweta's warm but direct tone

---

## CRITICAL: SOMERA Text Protection Strategy

### The Risk

**SOMERA Voice and SOMERA Text share the same backend function:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────┘

SOMERA Voice (VAPI) ─────┐
                         │
                         ├──► generate_somera_response()  ──► Response
                         │    (in somera_engine.py)
SOMERA Text (Web UI) ────┘
                         │
                         └──► Parameter: delivery_mode = "voice" or "text"
```

**If we modify `generate_somera_response()` without careful isolation, we will break SOMERA Text.**

This is not hypothetical - it is a certainty. Both products call the exact same function.

---

### Classification of Changes

Every proposed change falls into one of three categories:

#### Category A: SHARED (Affects Both - Intentional)

These changes improve both Voice and Text and should be applied universally:

| Change | Reason to Share |
|--------|-----------------|
| RAG retrieval improvements | Both need better coaching content |
| Pattern detection enhancements | Both need accurate pattern identification |
| Readiness scoring refinements | Both need to know user's readiness state |
| Safety guardrail updates | Both need crisis detection, PII filtering |
| Bug fixes in shared code | Both benefit from stability |

#### Category B: VOICE-ONLY (Must Be Isolated)

These changes are specific to voice delivery and MUST NOT affect Text:

| Change | Why Voice-Only | Text Behavior |
|--------|----------------|---------------|
| Max 2-3 sentences | Voice needs brevity | Text can be 4-6 sentences |
| Max 1 question per response | Voice is real-time | Text can have follow-ups |
| Style exemplar retrieval | Voice needs speech cadence | Text uses existing prompts |
| Strict validation + retry | Voice has latency constraints | Text is more flexible |
| Acknowledgment variety tracking | Voice repetition is jarring | Text less noticeable |
| Banned phrases ("I hear you") | Voice sounds scripted | Text is acceptable |

#### Category C: POTENTIALLY SHARED (Requires Discussion)

These changes MIGHT benefit both, but need Shweta's input:

| Change | Voice Benefit | Text Consideration |
|--------|---------------|-------------------|
| Turn-aware behavior | Yes - clear progression | Maybe - could help structure |
| Pattern naming timing | Yes - by Turn 3 | Maybe - depends on chat length |
| Discovery Call integration | Yes - natural handoff | Already works differently |

---

### Implementation Safeguards

#### Safeguard 1: Conditional Logic Pattern

Every Voice-only change MUST be wrapped in a delivery_mode check:

```python
def generate_somera_response(..., delivery_mode: str = "text"):
    
    # ═══════════════════════════════════════════════════════════
    # SHARED CODE: Runs for BOTH Voice and Text
    # ═══════════════════════════════════════════════════════════
    
    readiness_result = calculate_readiness_score(...)
    patterns = identify_emotional_patterns(...)
    rag_content = get_enhanced_coaching_context(...)
    
    # ═══════════════════════════════════════════════════════════
    # VOICE-ONLY CODE: Only runs when delivery_mode == "voice"
    # ═══════════════════════════════════════════════════════════
    
    if delivery_mode == "voice":
        # Voice-specific: Style exemplar retrieval
        style_examples = retrieve_style_exemplars(...)
        
        # Voice-specific: Dynamic prompt with strict constraints
        prompt = build_shweta_voice_prompt(
            rag_content=rag_content,
            style_examples=style_examples,
            max_sentences=3,
            max_questions=1
        )
        
        # Voice-specific: Validation with retry
        response = generate_with_validation(prompt, ...)
        
    else:
        # ═══════════════════════════════════════════════════════
        # TEXT MODE: Preserves existing behavior UNCHANGED
        # ═══════════════════════════════════════════════════════
        
        # Text uses existing prompt construction (no changes)
        prompt = build_existing_text_prompt(rag_content, ...)
        
        # Text uses existing generation (no validation layer)
        response = generate_response(prompt, ...)
    
    # ═══════════════════════════════════════════════════════════
    # SHARED POST-PROCESSING: Runs for BOTH Voice and Text
    # ═══════════════════════════════════════════════════════════
    
    response = apply_llm_critic(response, ...)
    response = filter_response_for_safety(response, ...)
    
    return response
```

#### Safeguard 2: Mandatory Text Testing

Before ANY deployment, we MUST run these Text mode tests:

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Basic greeting | "Hi, I'm feeling stuck" | Warm greeting + open question |
| Pattern discussion | "I always feel not good enough" | Empathetic exploration, can be multi-sentence |
| Long conversation | 6+ turns | Natural progression, multiple questions okay |
| Crisis signal | "I'm having dark thoughts" | Safety redirect to resources |
| Booking request | "How do I contact Shweta?" | Discovery Call link provided |

**These tests must pass BEFORE and AFTER every change.**

#### Safeguard 3: Separate Function Approach (Alternative)

If conditional logic becomes too complex, we can create entirely separate functions:

```python
# Option A: Single function with conditionals (proposed)
def generate_somera_response(..., delivery_mode="text"):
    if delivery_mode == "voice":
        return _generate_voice_response(...)
    else:
        return _generate_text_response(...)

# Option B: Separate entry points (fallback if needed)
def generate_somera_voice_response(...):
    # Voice-specific implementation
    pass

def generate_somera_text_response(...):
    # Unchanged existing implementation
    pass
```

We start with Option A. If it becomes unwieldy, we refactor to Option B.

#### Safeguard 4: Feature Flag (Emergency Rollback)

We can implement a feature flag to instantly disable Voice changes:

```python
VOICE_STYLE_ENABLED = True  # Set to False to disable all Voice changes

def generate_somera_response(..., delivery_mode="text"):
    
    if delivery_mode == "voice" and VOICE_STYLE_ENABLED:
        # New Voice behavior
        return _generate_enhanced_voice_response(...)
    elif delivery_mode == "voice":
        # Fallback: Old Voice behavior (same as Text)
        return _generate_legacy_response(...)
    else:
        # Text: Unchanged
        return _generate_text_response(...)
```

If Voice changes cause problems, we set `VOICE_STYLE_ENABLED = False` and redeploy.

---

### Testing Protocol

#### Phase 1: Before Any Code Changes

1. Record baseline Text responses for 5 test scenarios
2. Record baseline Voice responses for 5 test scenarios
3. Save these as "golden" reference outputs

#### Phase 2: After Each Implementation Phase

1. Run Text mode with same 5 scenarios
2. Compare to baseline - Text should be IDENTICAL
3. Run Voice mode with same 5 scenarios
4. Voice should show improvements (brevity, style, etc.)

#### Phase 3: Before Deployment

1. Full regression test on Text mode
2. Full test on Voice mode
3. Manual review of 3 Text transcripts
4. Manual review of 3 Voice transcripts
5. Shweta approval on Voice quality

---

### Decision Matrix for Each Change

When implementing any change, use this decision tree:

```
Is this change about:
│
├── RAG content/retrieval?
│   └── SHARED: Apply to both modes
│
├── Safety/guardrails?
│   └── SHARED: Apply to both modes
│
├── Response length/structure?
│   └── VOICE-ONLY: Wrap in delivery_mode check
│
├── Prompt construction style?
│   └── VOICE-ONLY: Wrap in delivery_mode check
│
├── Validation/retry logic?
│   └── VOICE-ONLY: Wrap in delivery_mode check
│
├── Turn/readiness awareness?
│   └── CHECK WITH SHWETA: May benefit both
│
└── Pattern naming timing?
    └── CHECK WITH SHWETA: May benefit both
```

---

### Summary: The Non-Negotiable Rules

1. **Every Voice-specific change MUST be wrapped in `if delivery_mode == "voice"`**
2. **Text mode MUST be tested before and after every change**
3. **Text behavior MUST remain unchanged unless explicitly approved**
4. **We MUST have a feature flag for emergency rollback**
5. **Deployment ONLY after Text regression tests pass**

Failure to follow these rules will break the existing SOMERA Text product.

---

## Proposed Solution Architecture

### The New Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     PROPOSED SOMERA FLOW                        │
└─────────────────────────────────────────────────────────────────┘

User Message
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: STATE DETECTION (existing - no changes needed)        │
├─────────────────────────────────────────────────────────────────┤
│ • Turn counter ──────► "This is Turn 3"                        │
│ • Readiness score ───► "User is at 45% (transition)"           │
│ • Pattern detection ─► "Detected: not_enough, prove_worth"     │
│ • Pillar detection ──► "Discussing: career"                    │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: SOLUTION RETRIEVAL (existing - no changes needed)     │
├─────────────────────────────────────────────────────────────────┤
│ • search_coaching_content_enhanced()                            │
│ • Returns Shweta's coaching content from ChromaDB               │
│ • This provides the WHAT to say                                 │
│                                                                 │
│ Example retrieved content:                                      │
│ "The prove-your-worth pattern often stems from early            │
│  experiences where love felt conditional on achievement..."     │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: STYLE RETRIEVAL (NEW - to be built)                   │
├─────────────────────────────────────────────────────────────────┤
│ • Query NEW ChromaDB collection: "shweta_voice_style"           │
│ • Retrieve 1-2 EXAMPLE exchanges matching current state:        │
│   - Turn phase: early (1-2), middle (3-4), late (5+)            │
│   - Readiness: explore, transition, guide                       │
│   - Pattern type: not_enough, prove_worth, etc.                 │
│                                                                 │
│ Example retrieved style:                                        │
│ "User: I'm always trying to prove myself at work.               │
│  Shweta: How long have you been carrying that pressure?"        │
│                                                                 │
│ IMPORTANT: These are examples of CADENCE, not phrases to copy   │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: DYNAMIC PROMPT CONSTRUCTION (NEW - to be built)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ASSEMBLED PROMPT:                                               │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ SECTION 1: BEHAVIORAL RULES (per turn/readiness)            │ │
│ │                                                             │ │
│ │ Turn 1-2 (Explore mode):                                    │ │
│ │ - Acknowledge briefly (under 10 words)                      │ │
│ │ - Ask ONE open question                                     │ │
│ │ - Focus on duration or body location                        │ │
│ │                                                             │ │
│ │ Turn 3-4 (Transition mode):                                 │ │
│ │ - Name the pattern you observe                              │ │
│ │ - Check if it resonates                                     │ │
│ │ - Use phrases like "I'm noticing..." or "Do you see..."     │ │
│ │                                                             │ │
│ │ Turn 5+ (Guide mode):                                       │ │
│ │ - Share ONE insight about why the pattern exists            │ │
│ │ - Offer Discovery Call naturally                            │ │
│ │ - Don't lecture - keep it brief                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ SECTION 2: CURRENT STATE                                    │ │
│ │                                                             │ │
│ │ "This is Turn 3. Readiness: 45% (transition).               │ │
│ │  Detected pattern: not_enough, prove_worth.                 │ │
│ │  Your task: Name the pattern you observe."                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ SECTION 3: SOLUTION CONTENT (from RAG)                      │ │
│ │                                                             │ │
│ │ [Shweta's actual coaching content about this pattern]       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ SECTION 4: STYLE EXAMPLES (from style collection)           │ │
│ │                                                             │ │
│ │ "Here's how Shweta responds in this phase:                  │ │
│ │                                                             │ │
│ │  Example 1:                                                 │ │
│ │  User: I feel like I'm always trying to prove myself.       │ │
│ │  Shweta: How long have you been carrying that pressure?     │ │
│ │                                                             │ │
│ │  Example 2:                                                 │ │
│ │  User: Nothing I do seems good enough.                      │ │
│ │  Shweta: Where do you feel that in your body right now?"    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ SECTION 5: HARD CONSTRAINTS (non-negotiable)                │ │
│ │                                                             │ │
│ │ - Maximum 2-3 sentences                                     │ │
│ │ - Ask only ONE question                                     │ │
│ │ - Do NOT start with "I hear you"                            │ │
│ │ - Do NOT use phrases like "It sounds like..."               │ │
│ │ - Do NOT ask multiple questions                             │ │
│ │ - Do NOT give unsolicited advice                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: LLM GENERATION                                        │
├─────────────────────────────────────────────────────────────────┤
│ • Send assembled prompt to gpt-4o-mini                          │
│ • Generate response                                             │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: STYLE VALIDATION (NEW - to be built)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Validation checks:                                              │
│ • Sentence count ≤ 3?                                           │
│ • Question count ≤ 1?                                           │
│ • Starts with "I hear you"? → FAIL                              │
│ • Contains "It sounds like"? → FAIL                             │
│ • Multiple questions? → FAIL                                    │
│                                                                 │
│ If validation fails:                                            │
│ • Log the failure reason                                        │
│ • Retry with stricter prompt (max 1 retry)                      │
│ • If still fails, use shortened version                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7: POST-PROCESSING (existing - minor enhancements)       │
├─────────────────────────────────────────────────────────────────┤
│ • apply_llm_critic() - existing                                 │
│ • filter_response_for_safety() - existing                       │
│ • Track acknowledgment history (new) - prevent repetition       │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
Final Response to User
```

---

## Implementation Phases

### Phase 1: Style Exemplar Collection (2-3 hours)

**Goal:** Create a curated set of Shweta's actual exchanges tagged by conversation phase.

**What we'll do:**
1. Extract 20-30 short exchanges from transcripts
2. Tag each exchange with metadata:
   - Turn phase: `early` (1-2), `middle` (3-4), `late` (5+)
   - Readiness: `explore`, `transition`, `guide`
   - Pattern: `not_enough`, `prove_worth`, `fear_of_judgment`, etc.
   - Type: `acknowledgment`, `pattern_naming`, `body_question`, `insight`, `handoff`
3. Create new ChromaDB collection: `shweta_voice_style`
4. Ingest tagged examples

**Example entries:**

```json
{
  "id": "style_001",
  "user_message": "I feel like I'm always trying to prove myself at work.",
  "shweta_response": "How long have you been carrying that pressure?",
  "turn_phase": "early",
  "readiness": "explore",
  "pattern": "prove_worth",
  "type": "body_question"
}

{
  "id": "style_002",
  "user_message": "Nothing I do is ever good enough for my mother.",
  "shweta_response": "You don't have separate problems. You have one pattern showing up everywhere. Do you see that?",
  "turn_phase": "middle",
  "readiness": "transition",
  "pattern": "not_enough",
  "type": "pattern_naming"
}

{
  "id": "style_003",
  "user_message": "I've never seen it that way before. You're right.",
  "shweta_response": "Now that you see this - are you ready to release it? This is exactly what we work on in live sessions.",
  "turn_phase": "late",
  "readiness": "guide",
  "pattern": "any",
  "type": "handoff"
}
```

**Source materials:**
- `transcripts/Final_Release_transcript.txt` (masterclass)
- `attached_assets/1_1_Session_Transcripts-_Sample_Data_1767169420281.md` (1:1 sessions)

**Files created/modified:**
- New: `shweta_style_exemplars.json` (curated examples)
- Modified: `chroma_manager.py` (add new collection)
- New: `ingest_style_exemplars.py` (ingestion script)

---

### Phase 2: Prompt Construction Service (2-3 hours)

**Goal:** Build a dynamic prompt assembler that creates turn-aware, readiness-aware prompts.

**What we'll do:**
1. Create `build_shweta_style_prompt()` function
2. Define behavioral rules per turn/readiness combination
3. Add style exemplar retrieval
4. Integrate with existing `generate_somera_response()`

**New function signature:**

```python
def build_shweta_style_prompt(
    turn_number: int,
    readiness_phase: str,  # "explore" | "transition" | "guide"
    detected_patterns: List[str],
    rag_content: str,
    style_examples: List[dict],
    conversation_history: List[dict]
) -> str:
    """
    Build a dynamic prompt that teaches the LLM Shweta's methodology
    for the current conversation state.
    
    Returns assembled prompt string.
    """
```

**Behavioral rules matrix:**

| Turn | Readiness | Primary Task | Question Style |
|------|-----------|--------------|----------------|
| 1-2 | Explore | Acknowledge + open question | "What's been happening?" |
| 1-2 | Transition | Acknowledge + body question | "Where do you feel that?" |
| 3-4 | Explore | Deepen + duration question | "How long have you carried this?" |
| 3-4 | Transition | Name the pattern | "I'm noticing a pattern..." |
| 3-4 | Guide | Pattern + readiness check | "Are you ready to release this?" |
| 5+ | Any | Insight + Discovery Call | "This is what Shweta works on..." |

**Files created/modified:**
- Modified: `somera_engine.py` (add prompt construction)
- New: `shweta_style_prompts.py` (behavioral rules and templates)

---

### Phase 3: Style Validator (1-2 hours)

**Goal:** Ensure generated responses meet Shweta's style criteria.

**What we'll do:**
1. Create `validate_shweta_style()` function
2. Implement hard constraint checking
3. Add retry logic for failed validations
4. Track acknowledgment history to prevent repetition

**Validation rules:**

```python
def validate_shweta_style(response: str, recent_acknowledgments: List[str]) -> dict:
    """
    Validate that response meets Shweta's style criteria.
    
    Returns:
        {
            "valid": bool,
            "issues": List[str],  # e.g., ["too_long", "multiple_questions"]
            "sentence_count": int,
            "question_count": int
        }
    """
    
    issues = []
    
    # Check sentence count (max 3)
    sentences = count_sentences(response)
    if sentences > 3:
        issues.append("too_long")
    
    # Check question count (max 1)
    questions = count_questions(response)
    if questions > 1:
        issues.append("multiple_questions")
    
    # Check for banned phrases
    banned = ["I hear you", "It sounds like", "I can sense", "That must be"]
    for phrase in banned:
        if phrase.lower() in response.lower():
            issues.append(f"banned_phrase:{phrase}")
    
    # Check for repeated acknowledgment
    acknowledgment = extract_acknowledgment(response)
    if acknowledgment and acknowledgment in recent_acknowledgments[-3:]:
        issues.append("repeated_acknowledgment")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "sentence_count": sentences,
        "question_count": questions
    }
```

**Files created/modified:**
- New: `style_validator.py`
- Modified: `somera_engine.py` (integrate validation)

---

### Phase 4: Integration & Wiring (1-2 hours)

**Goal:** Connect all new components into the existing flow WITH PROPER TEXT PROTECTION.

**What we'll do:**
1. Modify `generate_somera_response()` with `delivery_mode` conditional logic
2. Add style exemplar retrieval FOR VOICE ONLY
3. Integrate validation with retry logic FOR VOICE ONLY
4. Add acknowledgment history tracking FOR VOICE ONLY
5. Add feature flag `VOICE_STYLE_ENABLED` for emergency rollback

**CRITICAL: Modified flow in `somera_engine.py`:**

```python
# Feature flag for emergency rollback
VOICE_STYLE_ENABLED = True

def generate_somera_response(..., delivery_mode: str = "text"):
    
    # ═══════════════════════════════════════════════════════════════
    # SHARED CODE: Runs for BOTH Voice and Text (no changes here)
    # ═══════════════════════════════════════════════════════════════
    
    readiness_result = calculate_readiness_score(...)
    patterns = identify_emotional_patterns(...)
    turn_number = count_conversation_turns(...)
    
    enhanced_context = get_enhanced_coaching_context(...)
    rag_content = format_coaching_context(enhanced_context["documents"])
    
    # ═══════════════════════════════════════════════════════════════
    # VOICE-ONLY CODE: Only runs when delivery_mode == "voice"
    # ═══════════════════════════════════════════════════════════════
    
    if delivery_mode == "voice" and VOICE_STYLE_ENABLED:
        # Voice-specific: Get style examples
        style_examples = retrieve_style_exemplars(
            turn_phase=get_turn_phase(turn_number),
            readiness=readiness_result["recommendation"],
            patterns=[p.pattern_id for p in patterns[:2]]
        )
        
        # Voice-specific: Build dynamic prompt with strict constraints
        prompt = build_shweta_voice_prompt(
            turn_number=turn_number,
            readiness_phase=readiness_result["recommendation"],
            detected_patterns=patterns,
            rag_content=rag_content,
            style_examples=style_examples,
            conversation_history=conversation_history,
            max_sentences=3,
            max_questions=1
        )
        
        # Voice-specific: Generate with validation
        response = call_llm(prompt, ...)
        
        # Voice-specific: Validate style
        validation = validate_shweta_style(response, recent_acknowledgments)
        if not validation["valid"]:
            response = retry_with_stricter_prompt(...)
    
    else:
        # ═══════════════════════════════════════════════════════════
        # TEXT MODE (or Voice with feature flag OFF): UNCHANGED
        # ═══════════════════════════════════════════════════════════
        
        # Use existing prompt construction - NO CHANGES
        prompt = get_existing_text_prompt(...)
        response = call_llm(prompt, ...)
    
    # ═══════════════════════════════════════════════════════════════
    # SHARED POST-PROCESSING: Runs for BOTH Voice and Text
    # ═══════════════════════════════════════════════════════════════
    
    response = apply_llm_critic(response, ...)
    response = filter_response_for_safety(response, ...)
    
    return response
```

**Files modified:**
- `somera_engine.py` (main integration)
- `webhook_server.py` (if VAPI-specific changes needed)

---

### Phase 5: Testing & Validation (2-3 hours)

**Goal:** Ensure the new system works correctly, achieves 90% Voice fidelity, AND does not break Text mode.

**What we'll do:**

#### 5a. MANDATORY: Text Regression Tests (BEFORE anything else)

Run these 5 scenarios in TEXT mode and verify behavior is UNCHANGED:

| # | Test Input | Expected Text Behavior | Pass/Fail |
|---|------------|------------------------|-----------|
| 1 | "Hi, I'm feeling stuck lately" | Warm greeting + open exploration | ☐ |
| 2 | "I always feel not good enough" | Empathetic response, 3-6 sentences okay | ☐ |
| 3 | "I'm having dark thoughts about harming myself" | Crisis redirect to resources | ☐ |
| 4 | "How do I contact Shweta?" | Discovery Call link provided | ☐ |
| 5 | Multi-turn (6+ exchanges) | Natural progression, no forced brevity | ☐ |

**ALL 5 must pass before proceeding. If ANY fail, stop and debug.**

#### 5b. Unit tests (Voice-specific components):

- Test prompt construction with various states
- Test style validation with edge cases
- Test exemplar retrieval
- Test feature flag toggle behavior

#### 5c. Voice Integration tests:

| Scenario | Turn | Readiness | Expected Voice Behavior |
|----------|------|-----------|-------------------------|
| First contact | 1 | Explore | Brief acknowledge + open question (≤3 sentences) |
| Deepening | 2 | Explore | Body/duration question (1 question only) |
| Pattern spotted | 3 | Transition | Name the pattern |
| Breakthrough | 4 | Guide | Readiness check |
| Ready for handoff | 5 | Guide | Discovery Call offer |
| Crisis signal | Any | Any | Safety redirect |
| Closure signal | Any | Any | Warm goodbye |

#### 5d. Fidelity testing:

- Compare outputs against Shweta's actual responses
- Measure: brevity, question count, pattern naming timing
- Shweta reviews 3+ sample Voice transcripts

---

### Phase 6: Deployment (1 hour)

**Goal:** Deploy changes safely with ability to rollback, ensuring Text mode remains stable.

**Pre-deployment checklist:**
- [ ] Text regression tests passed
- [ ] Voice integration tests passed
- [ ] Feature flag `VOICE_STYLE_ENABLED = True` verified
- [ ] Shweta approved sample Voice outputs

**Deployment steps:**
1. Final Text regression test (one more time)
2. Merge `somera-voice-improvements` branch to `main`
3. Restart workflows
4. Test Text mode immediately after restart
5. Test Voice mode via VAPI call
6. Monitor logs for errors
7. Get Shweta's feedback

**Rollback plan:**

| Issue Level | Action |
|-------------|--------|
| Critical (Text broken) | `git checkout main && restart workflows` |
| Severe (Voice broken) | Set `VOICE_STYLE_ENABLED = False` and redeploy |
| Minor (Voice needs tuning) | Fix on branch, test, redeploy |

---

## Technical Specifications

### New Files to Create

| File | Purpose | Location |
|------|---------|----------|
| `shweta_style_exemplars.json` | Curated style examples | `/data/` |
| `shweta_style_prompts.py` | Behavioral rules & templates | `/` |
| `style_validator.py` | Response validation | `/` |
| `ingest_style_exemplars.py` | Ingestion script | `/` |

### Files to Modify

| File | Changes |
|------|---------|
| `somera_engine.py` | Add prompt construction, style retrieval, validation |
| `chroma_manager.py` | Add `shweta_voice_style` collection |
| `webhook_server.py` | Minor changes for VAPI-specific handling if needed |

### New ChromaDB Collection

**Collection:** `shweta_voice_style`

**Schema:**
```
{
  "id": str,
  "user_message": str,           # What the user said
  "shweta_response": str,        # How Shweta responded
  "turn_phase": str,             # "early" | "middle" | "late"
  "readiness": str,              # "explore" | "transition" | "guide"
  "pattern": str,                # Pattern ID or "any"
  "type": str,                   # "acknowledgment" | "pattern_naming" | "body_question" | "insight" | "handoff"
  "embedding": vector            # For semantic similarity
}
```

---

## Risk Assessment

### CRITICAL RISK: SOMERA Text Interference

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Voice changes break Text mode | HIGH if not managed | SEVERE - breaks production product | See [SOMERA Text Protection Strategy](#critical-somera-text-protection-strategy) |

**This is the #1 risk of this project.** All code changes MUST:
1. Be wrapped in `if delivery_mode == "voice"` conditionals
2. Pass Text regression tests before deployment
3. Have feature flag for emergency rollback

### High Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing SOMERA Text | Users see broken responses | Follow Text Protection Strategy, test both modes, use feature flag |
| Breaking existing SOMERA Voice | VAPI calls fail | Keep webhook endpoint unchanged, incremental changes |
| ChromaDB corruption | All coaching knowledge lost | Backup before changes, use separate collection for style |

### Medium Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Style validation too strict | Good responses rejected | Start with lenient rules, tighten later |
| Exemplar retrieval slow | Increased latency | Limit to 2 examples, cache common queries |
| Pattern naming too aggressive | Feels scripted | Test with real users, adjust turn threshold |
| Conditional logic becomes complex | Hard to maintain | Consider refactor to separate functions (Option B) |

### Low Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Shweta doesn't like output | Needs iteration | Framework document as reference, iterate |
| Acknowledgment variety insufficient | Still sounds repetitive | Expand variety list |

---

## Success Criteria

### Quantitative

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Response length | ≤3 sentences | Automated check |
| Questions per response | ≤1 | Automated check |
| Pattern named by turn | Turn 3-4 | Conversation analysis |
| "I hear you" usage | ≤1 per 5 responses | Text search |
| Discovery Call conversion | ≥ current rate | Analytics |

### Qualitative

| Criteria | How to Evaluate |
|----------|-----------------|
| Feels like Shweta | Shweta's direct feedback |
| Warm but not verbose | User feedback |
| Insightful pattern naming | Shweta's review of transcripts |
| Natural Discovery Call bridge | Listen to call recordings |

---

## Rollback Plan

### Before Starting
1. Note current checkpoint: `c8d685e80b31db80fcbf35a72bd3af43eaceaaac`
2. Confirm on branch: `somera-voice-improvements`
3. Ensure `main` branch is stable

### If Something Goes Wrong

**Level 1: Minor issues**
- Fix on current branch
- Redeploy

**Level 2: Significant issues**
```bash
git checkout main
# Restart workflows
```

**Level 3: Critical issues**
- Use Replit's checkpoint rollback feature
- Return to checkpoint before changes

### Post-Deployment Monitoring

1. Watch SOMERA Voice call logs for errors
2. Check response latency (should be <2s additional)
3. Review first 10 transcripts manually
4. Get Shweta's feedback within 24 hours

---

## Questions for Shweta

Before implementation, we need Shweta's input on:

### Methodology Questions

1. **Pattern naming timing:** Is Turn 3 the right time to name the pattern, or should it be earlier/later?

2. **Readiness thresholds:** Current thresholds are:
   - Explore: <35%
   - Transition: 35-70%
   - Guide: >70%
   
   Do these feel right for when to offer Discovery Call?

3. **Body awareness questions:** Which questions resonate most with your style?
   - "Where do you feel that in your body?"
   - "How long have you been carrying this?"
   - "What does that feel like physically?"

4. **Pattern language:** Review the pattern naming library in `SOMERA_VOICE_FRAMEWORK_COMPLETED.md`. Are these phrases accurate to your methodology?

### Style Questions

5. **Banned phrases:** We're planning to ban:
   - "I hear you"
   - "It sounds like"
   - "I can sense"
   - "That must be"
   
   Are there others to add? Any to remove?

6. **Opening style:** What's your preferred way to open a coaching conversation when someone shares something heavy?

7. **Discovery Call bridge:** What's your natural way of offering a Discovery Call when someone is ready?

### Content Questions

8. **Missing content:** After reviewing the framework document, is there coaching content we should add to the knowledge base?

9. **Example exchanges:** Are the extracted examples in the framework document accurate representations of your style?

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Review by Shweta | 1-2 days | This document |
| Phase 1: Style Exemplars | 2-3 hours | Shweta approval |
| Phase 2: Prompt Construction | 2-3 hours | Phase 1 complete |
| Phase 3: Style Validator | 1-2 hours | Can parallel with Phase 2 |
| Phase 4: Integration | 1-2 hours | Phases 2 & 3 complete |
| Phase 5: Testing | 2-3 hours | Phase 4 complete |
| Phase 6: Deployment | 1 hour | Testing passed |

**Total implementation time:** ~10-14 hours (after Shweta approval)

---

## Appendix: File Locations

### Source Materials
- `transcripts/Final_Release_transcript.txt` - Masterclass transcript
- `attached_assets/1_1_Session_Transcripts-_Sample_Data_1767169420281.md` - 1:1 sessions

### Framework Documents
- `docs/SOMERA_VOICE_FRAMEWORK_COMPLETED.md` - Shweta's phrases and methodology
- `docs/SOMERA_VOICE_RESTRUCTURE_FRAMEWORK.md` - Empty template for future use

### Core Engine Files
- `somera_engine.py` - Main SOMERA logic
- `webhook_server.py` - VAPI webhook handling
- `readiness_scoring.py` - Readiness detection
- `emotional_patterns.py` - Pattern detection
- `knowledge_base.py` - RAG retrieval
- `chroma_manager.py` - ChromaDB management
- `safety_guardrails.py` - Safety filters

### Memory/Context
- `replit.md` - Project documentation and memory
