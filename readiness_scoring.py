"""
Readiness Scoring System for SOMERA

This module implements a weighted heuristic system to detect when a user is ready
to transition from exploration/questioning to receiving guidance and solutions.

Based on patterns observed in Shweta's 1:1 coaching sessions:
1. Breakthrough insights - "I realized", "I see now", etc.
2. Confusion/stuck signals - "I don't know", "I'm lost", etc.
3. Emotional exhaustion - Short responses, fatigue cues
4. Repetition detection - Restating the same issue multiple times
5. Explicit requests - Already handled by solution mode detection
6. Sensing language - Phrases Shweta uses before transitioning
"""

from typing import List, Tuple, Dict
import re


BREAKTHROUGH_PATTERNS = [
    r"\bi realized\b",
    r"\bi see now\b",
    r"\bit hit me\b",
    r"\bit makes sense\b",
    r"\bthat makes sense\b",
    r"\bi understand now\b",
    r"\bi get it\b",
    r"\bi finally understand\b",
    r"\bthis is my journey\b",
    r"\bi need to\b",
    r"\bi have to\b",
    r"\bi should\b",
    r"\bi can see\b",
    r"\bwow\b",
    r"\boh\b.*\bi see\b",
    r"\bnever thought of it\b",
    r"\bnever looked at it\b",
    r"\byou're right\b",
    r"\bthat's true\b",
    r"\bi didn't realize\b",
    r"\bi'm realizing\b",
]

CONFUSION_STUCK_PATTERNS = [
    r"\bi don'?t know\b",
    r"\bdon'?t know\b",
    r"\bdon'?t know what to do\b",
    r"\bi have no idea\b",
    r"\bhave no idea\b",
    r"\bno idea\b",
    r"\bi'm stuck\b",
    r"\bfeeling stuck\b",
    r"\bi feel stuck\b",
    r"\bi feel lost\b",
    r"\bi'm lost\b",
    r"\bi don'?t understand\b",
    r"\bi'm confused\b",
    r"\bconfused\b",
    r"\bwhat should i do\b",
    r"\bwhat do i do\b",
    r"\bwhat can i do\b",
    r"\bi can'?t figure\b",
    r"\bcan'?t figure\b",
    r"\btrying to figure\b",
    r"\bcan'?t see\b.*\bway\b",
    r"\bno clue\b",
    r"\bit'?s overwhelming\b",
    r"\bfeeling overwhelmed\b",
    r"\btoo much\b",
    r"\bcan'?t cope\b",
    r"\bcan'?t handle\b",
    r"\bgoing in circles\b",
    r"\bsame problem\b",
    r"\bkeep coming back to\b",
    r"\bi need help\b",
    r"\bhelp me\b",
    r"\bcan you help\b",
    r"\byou can help\b",
    r"\bmaybe you can\b",
    r"\bsomething you can\b",
    r"\banything you can\b",
]

EXHAUSTION_PATTERNS = [
    r"\bi'm tired\b",
    r"\bi'm exhausted\b",
    r"\bjust tired\b",
    r"\bso tired\b",
    r"\bbeen too much\b",
    r"\bjust been too much\b",
    r"\bi can'?t anymore\b",
    r"\bcan'?t do this anymore\b",
    r"\bgiven up\b",
    r"\bi honestly can'?t\b",
    r"\bdon'?t remember\b.*\bhappy\b",
    r"\bweighed down\b",
    r"\boverburdened\b",
    r"\bburned out\b",
    r"\bburnout\b",
    r"\bdrained\b",
    r"\bno energy\b",
    r"\bjust want it to stop\b",
]

ENGAGEMENT_DROP_PATTERNS = [
    r"^(yes|no|ok|okay|sure|maybe|i guess|idk|i don'?t know|fine|alright)[\.\?!]?$",
    r"^(hmm|hm|mhm|uh huh|yeah|yep|nope)[\.\?!]?$",
]


def calculate_breakthrough_score(message: str) -> float:
    """Calculate breakthrough insight score (0-1)."""
    message_lower = message.lower()
    matches = sum(1 for pattern in BREAKTHROUGH_PATTERNS if re.search(pattern, message_lower))
    return min(1.0, matches * 0.4)


def calculate_confusion_score(message: str) -> float:
    """Calculate confusion/stuck score (0-1)."""
    message_lower = message.lower()
    matches = sum(1 for pattern in CONFUSION_STUCK_PATTERNS if re.search(pattern, message_lower))
    return min(1.0, matches * 0.25)


def calculate_exhaustion_score(message: str) -> float:
    """Calculate emotional exhaustion score (0-1)."""
    message_lower = message.lower()
    matches = sum(1 for pattern in EXHAUSTION_PATTERNS if re.search(pattern, message_lower))
    return min(1.0, matches * 0.35)


def calculate_engagement_drop_score(message: str) -> float:
    """Calculate engagement drop score based on short/disengaged responses."""
    message_stripped = message.strip().lower()
    
    for pattern in ENGAGEMENT_DROP_PATTERNS:
        if re.match(pattern, message_stripped):
            return 0.6
    
    if len(message_stripped) < 15:
        return 0.3
    if len(message_stripped) < 30:
        return 0.1
    
    return 0.0


def detect_repetition(conversation_history: List[dict], current_message: str) -> float:
    """
    Detect if user is repeating the same topic/issue.
    Returns a score 0-1 based on repetition level.
    """
    if not conversation_history:
        return 0.0
    
    user_messages = [
        msg.get("content", "").lower() 
        for msg in conversation_history 
        if msg.get("role") == "user"
    ]
    
    if len(user_messages) < 2:
        return 0.0
    
    current_lower = current_message.lower()
    current_words = set(re.findall(r'\b\w{4,}\b', current_lower))
    
    if not current_words:
        return 0.0
    
    repetition_count = 0
    for prev_msg in user_messages[-4:]:
        prev_words = set(re.findall(r'\b\w{4,}\b', prev_msg))
        if prev_words:
            overlap = len(current_words & prev_words) / max(len(current_words), 1)
            if overlap > 0.4:
                repetition_count += 1
    
    return min(1.0, repetition_count * 0.35)


def calculate_conversation_depth_score(conversation_history: List[dict]) -> float:
    """
    Score based on conversation depth.
    Early turns = more questioning, Later turns = more guidance.
    """
    if not conversation_history:
        return 0.0
    
    user_turns = sum(1 for msg in conversation_history if msg.get("role") == "user")
    
    if user_turns <= 2:
        return 0.0
    elif user_turns <= 4:
        return 0.2
    elif user_turns <= 6:
        return 0.4
    elif user_turns <= 8:
        return 0.6
    else:
        return 0.8


EXPLICIT_SOLUTION_PATTERNS = [
    r"\bgive me (?:a )?solution\b",
    r"\bhelp me\b",
    r"\bi need help\b",
    r"\btell me what(?:'s| is)? (?:going on|wrong|the problem)\b",
    r"\bwhat(?:'s| is)? (?:the problem|wrong|going on)\b",
    r"\bhow would i know\b",
    r"\bthat(?:'s| is)? why i(?:'m| am) asking you\b",
    r"\bjust tell me\b",
    r"\bjust give me\b",
    r"\bstop asking questions\b",
    r"\banswer (?:my question|me)\b",
    r"\bi(?:'m| am) asking you\b",
    r"\bplease help\b",
    r"\bcan you help\b",
    r"\bwhat should i do\b",
    r"\bwhat can i do\b",
    r"\bwhat do you suggest\b",
    r"\bwhat do you think\b",
    r"\byour suggestion\b",
    r"\bgive me (?:some )?(?:steps|guidance|pointers|tips)\b",
    r"\bcertain (?:steps|pointers|tips)\b",
    r"\bi(?:'m| am) open\b",
    r"\bopen to (?:everything|anything|that)\b",
    r"\bi need your (?:help|guidance|advice)\b",
    r"\byou can (?:help|assist|guide)\b",
    r"\bcan you (?:assist|guide)\b",
]

def detect_explicit_solution_request(message: str) -> bool:
    """
    Fast-path detection for explicit solution requests.
    When user directly asks for help/solution, skip the scoring and go to guide mode.
    """
    message_lower = message.lower()
    for pattern in EXPLICIT_SOLUTION_PATTERNS:
        if re.search(pattern, message_lower):
            return True
    return False


def check_prior_guide_mode(conversation_history: List[dict]) -> bool:
    """
    Check if any previous message in the conversation triggered guide mode.
    This provides 'stickiness' - once user enters guide mode, we stay there
    unless they explicitly retreat.
    
    Returns True if guide mode was previously activated.
    """
    if not conversation_history:
        return False
    
    for msg in conversation_history:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if detect_explicit_solution_request(content):
                return True
    
    return False


def calculate_readiness_score(
    current_message: str,
    conversation_history: List[dict] = None
) -> Dict:
    """
    Calculate overall readiness score for transitioning to guidance mode.
    
    NEW: Includes "stickiness" - once guide mode is activated by an explicit request,
    it remains active for the rest of the conversation unless user explicitly retreats.
    
    Returns:
        Dict with:
        - total_score: Overall readiness (0-1)
        - is_ready: Boolean - ready to transition?
        - components: Individual score components
        - recommendation: "explore", "transition", or "guide"
    """
    if conversation_history is None:
        conversation_history = []
    
    # FAST-PATH: Explicit solution requests immediately trigger guide mode
    if detect_explicit_solution_request(current_message):
        return {
            "total_score": 0.90,
            "is_ready": True,
            "recommendation": "guide",
            "components": {
                "breakthrough": 0.0,
                "confusion": 0.0,
                "exhaustion": 0.0,
                "engagement_drop": 0.0,
                "repetition": 0.0,
                "depth": 0.0,
            },
            "explicit_request": True,
            "sticky_guide": False
        }
    
    # STICKINESS: If user previously triggered guide mode, maintain it
    prior_guide = check_prior_guide_mode(conversation_history)
    if prior_guide:
        return {
            "total_score": 0.70,
            "is_ready": True,
            "recommendation": "guide",
            "components": {
                "breakthrough": 0.0,
                "confusion": 0.0,
                "exhaustion": 0.0,
                "engagement_drop": 0.0,
                "repetition": 0.0,
                "depth": 0.0,
            },
            "explicit_request": False,
            "sticky_guide": True
        }
    
    breakthrough = calculate_breakthrough_score(current_message)
    confusion = calculate_confusion_score(current_message)
    exhaustion = calculate_exhaustion_score(current_message)
    engagement_drop = calculate_engagement_drop_score(current_message)
    repetition = detect_repetition(conversation_history, current_message)
    depth = calculate_conversation_depth_score(conversation_history)
    
    weighted_score = (
        breakthrough * 0.25 +      # Breakthrough signals
        confusion * 0.20 +          # Confusion/stuck
        exhaustion * 0.20 +         # Emotional exhaustion
        engagement_drop * 0.10 +    # Disengagement
        repetition * 0.15 +         # Repetition
        depth * 0.10                # Conversation depth
    )
    
    if breakthrough >= 0.35:
        weighted_score += 0.20
    
    if confusion >= 0.25:
        weighted_score += 0.10
        if depth >= 0.2:
            weighted_score += 0.10
    
    if exhaustion >= 0.35:
        weighted_score += 0.15
    
    if confusion >= 0.4:
        weighted_score += 0.10
    
    total_score = min(1.0, weighted_score)
    
    if total_score >= 0.35:
        recommendation = "guide"
        is_ready = True
    elif total_score >= 0.20:
        recommendation = "transition"
        is_ready = True
    else:
        recommendation = "explore"
        is_ready = False
    
    return {
        "total_score": round(total_score, 3),
        "is_ready": is_ready,
        "recommendation": recommendation,
        "components": {
            "breakthrough": round(breakthrough, 3),
            "confusion": round(confusion, 3),
            "exhaustion": round(exhaustion, 3),
            "engagement_drop": round(engagement_drop, 3),
            "repetition": round(repetition, 3),
            "depth": round(depth, 3),
        }
    }


def get_transition_context(readiness_result: Dict) -> str:
    """
    Generate context for the LLM based on readiness assessment.
    This is injected into the SOMERA system prompt.
    """
    score = readiness_result["total_score"]
    rec = readiness_result["recommendation"]
    components = readiness_result["components"]
    
    if rec == "explore":
        return ""
    
    signals = []
    if components["breakthrough"] >= 0.3:
        signals.append("The user has expressed a breakthrough or insight")
    if components["confusion"] >= 0.25:
        signals.append("The user is expressing confusion or feeling stuck")
    if components["exhaustion"] >= 0.35:
        signals.append("The user is showing signs of emotional exhaustion")
    if components["repetition"] >= 0.35:
        signals.append("The user is circling back to the same issue")
    if components["engagement_drop"] >= 0.3:
        signals.append("The user's responses are becoming shorter")
    if components["depth"] >= 0.6:
        signals.append("This conversation has had significant exploration")
    
    if rec == "transition":
        return f"""
=== READINESS SIGNAL DETECTED (Score: {score:.0%}) ===
{chr(10).join(f'- {s}' for s in signals)}

Consider: Gently begin to offer perspective or insights while still honoring their experience.
You might say: "Based on what you've shared..." or "I sense you might be ready to explore some perspectives on this..."
Balance: 60% acknowledgment, 40% gentle guidance."""
    
    else:  # guide
        return f"""
=== TRANSITION TO GUIDANCE RECOMMENDED (Score: {score:.0%}) ===
{chr(10).join(f'- {s}' for s in signals)}

The user appears ready to receive guidance. Shift your approach:
- Lead with a brief acknowledgment (1-2 sentences)
- Then provide 2-3 concrete insights from the coaching content
- Be direct and give them something valuable to take away
- End with an invitation to explore further or connect with Shweta

Balance: 30% acknowledgment, 70% actionable guidance."""


if __name__ == "__main__":
    test_cases = [
        ("Hi, I'm feeling stressed about work", []),
        ("I don't know what to do anymore, I'm stuck", []),
        ("I realized something - this is about my fear of rejection", []),
        ("yeah", [{"role": "user", "content": "I'm unhappy"}, {"role": "assistant", "content": "Tell me more"}]),
        ("It's just been too much. I'm so tired.", []),
        ("I keep dealing with the same problem at work", [
            {"role": "user", "content": "My boss doesn't respect me"},
            {"role": "assistant", "content": "How does that make you feel?"},
            {"role": "user", "content": "I feel disrespected at work all the time"},
        ]),
        ("What should I do about my relationship?", [
            {"role": "user", "content": "I'm in a difficult relationship"},
            {"role": "assistant", "content": "Tell me more about that"},
            {"role": "user", "content": "My partner is unavailable"},
            {"role": "assistant", "content": "How does that affect you?"},
            {"role": "user", "content": "I feel lonely and sad"},
            {"role": "assistant", "content": "That sounds difficult"},
        ]),
    ]
    
    print("=" * 60)
    print("READINESS SCORING SYSTEM TESTS")
    print("=" * 60)
    
    for msg, history in test_cases:
        result = calculate_readiness_score(msg, history)
        print(f"\nMessage: '{msg[:50]}...'")
        print(f"  History: {len(history)} messages")
        print(f"  Score: {result['total_score']:.1%}")
        print(f"  Ready: {result['is_ready']} | Recommendation: {result['recommendation']}")
        print(f"  Components: {result['components']}")
