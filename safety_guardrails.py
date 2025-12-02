"""
Safety Guardrails Module for JoveHeal Chatbot

This module implements strict safety filters to ensure the chatbot:
- Does NOT provide medical, psychological, psychiatric, or therapeutic advice
- Detects and redirects high-risk emotional/mental health queries
- Stays within the realm of general mindset coaching and wellness information
"""

import re
from typing import Tuple

JOVEHEAL_PROGRAM_URLS = {
    "Balance Mastery": "https://joveheal.com/balance-mastery/",
    "Inner Mastery Lounge": "https://joveheal.com/inner-mastery-lounge/",
    "Elevate 360": "https://joveheal.com/elevate-360/",
    "Relationship Healing": "https://joveheal.com/relationship-healing/",
    "Career Healing": "https://joveheal.com/career-healing/",
    "Beyond the Hustle": "https://joveheal.com/beyond-the-hustle/",
    "Inner Reset": "https://joveheal.com/inner-reset/",
    "Shed & Shine": "https://joveheal.com/shed-and-shine/",
    "Services": "https://joveheal.com/services/",
    "About": "https://joveheal.com/about/",
    "Testimonials": "https://joveheal.com/testimonials/",
    "Contact": "https://joveheal.com/contact/",
    "Homepage": "https://joveheal.com/",
}

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die", 
    "don't want to live", "self-harm", "self harm", "hurt myself",
    "cutting myself", "overdose", "ending it all", "no reason to live",
    "better off dead", "can't go on", "goodbye forever"
]

MENTAL_HEALTH_KEYWORDS = [
    "depression", "depressed", "anxiety disorder", "panic attack",
    "ptsd", "post-traumatic", "bipolar", "schizophrenia", "psychosis",
    "eating disorder", "anorexia", "bulimia", "ocd", "obsessive compulsive",
    "borderline personality", "dissociative", "hallucination", "delusion",
    "manic episode", "mental illness", "mental disorder", "psychiatric"
]

MEDICAL_KEYWORDS = [
    "medication", "medicine", "prescription", "dosage", "side effects",
    "symptoms", "diagnosis", "diagnose", "treatment", "therapy",
    "antidepressant", "antipsychotic", "benzodiazepine", "ssri",
    "blood pressure", "heart condition", "diabetes", "cancer",
    "chronic pain", "disease", "medical condition", "doctor said",
    "should i stop taking", "should i start taking", "drug interaction"
]

ABUSE_VIOLENCE_KEYWORDS = [
    "abuse", "abused", "abusive", "domestic violence", "being hit",
    "physical abuse", "sexual abuse", "emotional abuse", "assault",
    "rape", "molest", "threatening me", "violence", "violent"
]

EXTREME_DISTRESS_KEYWORDS = [
    "can't cope", "breaking down", "complete breakdown", "losing my mind",
    "going crazy", "can't take it anymore", "overwhelmed", "desperate",
    "hopeless", "helpless", "worthless", "no way out", "trapped",
    "scared for my life", "in danger"
]

SAFE_REDIRECT_RESPONSE = """I hear you, and I'm really sorry you're going through this. What you're describing sounds like something that deserves real, professional support.

I'm here to share information about JoveHeal's programs and general mindset coaching, but I'm not equipped to provide medical or mental health guidance.

**Please reach out to qualified professionals:**
- **Emergency:** Call 911 or your local emergency services
- **Crisis Support:** National Suicide Prevention Lifeline: 988 (US)
- **Mental Health:** Contact a licensed therapist or counselor
- **Medical Concerns:** Please consult with your doctor

You deserve proper care and support. Is there anything about JoveHeal's programs I can help you with?"""

MEDICAL_REDIRECT_RESPONSE = """I appreciate you sharing that with me. However, I'm not able to provide medical advice, diagnose conditions, or make recommendations about medications or treatments.

For any health-related concerns, please consult with a qualified healthcare professional who can give you personalized guidance.

I'm here to share information about JoveHeal's wellness programs, coaching services, and mindset-focused offerings. Is there something specific about our services I can help you with?"""

THERAPY_REDIRECT_RESPONSE = """Thank you for sharing that. What you're describing sounds like it would benefit from professional support from a licensed therapist or counselor.

While JoveHeal offers mindset coaching and wellness programs, we're not a substitute for professional mental health care when it's needed.

I'd encourage you to reach out to a mental health professional who can provide proper support.

In the meantime, I'm happy to share information about JoveHeal's programs if you'd like to know more about our mindset coaching and wellness offerings."""


def check_for_crisis_content(message: str) -> Tuple[bool, str]:
    """
    Check if the message contains crisis-related content.
    Returns (is_crisis, redirect_response)
    """
    message_lower = message.lower()
    
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return True, SAFE_REDIRECT_RESPONSE
    
    return False, ""


def check_for_mental_health_content(message: str) -> Tuple[bool, str]:
    """
    Check if the message is asking for mental health advice.
    Returns (is_mental_health, redirect_response)
    """
    message_lower = message.lower()
    
    advice_patterns = [
        r"how (do|can|should) i (deal|cope|handle|manage|treat|fix|cure)",
        r"what should i do about my",
        r"how to (get rid of|overcome|treat|cure|heal from)",
        r"am i (depressed|anxious|mentally ill|crazy)",
        r"do i have (depression|anxiety|ptsd|bipolar|ocd)"
    ]
    
    for keyword in MENTAL_HEALTH_KEYWORDS:
        if keyword in message_lower:
            for pattern in advice_patterns:
                if re.search(pattern, message_lower):
                    return True, THERAPY_REDIRECT_RESPONSE
            if any(q in message_lower for q in ["help me with", "what should", "how do i", "can you help"]):
                return True, THERAPY_REDIRECT_RESPONSE
    
    return False, ""


def check_for_medical_content(message: str) -> Tuple[bool, str]:
    """
    Check if the message is asking for medical advice.
    Returns (is_medical, redirect_response)
    """
    message_lower = message.lower()
    
    for keyword in MEDICAL_KEYWORDS:
        if keyword in message_lower:
            if any(q in message_lower for q in ["should i", "can i", "is it safe", "what happens if", "recommend", "suggest"]):
                return True, MEDICAL_REDIRECT_RESPONSE
    
    return False, ""


def check_for_abuse_violence(message: str) -> Tuple[bool, str]:
    """
    Check if the message describes abuse or violence.
    Returns (is_abuse, redirect_response)
    """
    message_lower = message.lower()
    
    for keyword in ABUSE_VIOLENCE_KEYWORDS:
        if keyword in message_lower:
            return True, SAFE_REDIRECT_RESPONSE
    
    return False, ""


def check_for_extreme_distress(message: str) -> Tuple[bool, str]:
    """
    Check if the message indicates extreme emotional distress.
    Returns (is_distress, redirect_response)
    """
    message_lower = message.lower()
    
    distress_count = sum(1 for keyword in EXTREME_DISTRESS_KEYWORDS if keyword in message_lower)
    
    if distress_count >= 2:
        return True, SAFE_REDIRECT_RESPONSE
    
    return False, ""


def apply_safety_filters(message: str) -> Tuple[bool, str]:
    """
    Apply all safety filters to the message.
    Returns (should_redirect, redirect_response)
    
    If should_redirect is True, the chatbot should return the redirect_response
    instead of processing the query through the RAG system.
    """
    is_crisis, crisis_response = check_for_crisis_content(message)
    if is_crisis:
        return True, crisis_response
    
    is_abuse, abuse_response = check_for_abuse_violence(message)
    if is_abuse:
        return True, abuse_response
    
    is_distress, distress_response = check_for_extreme_distress(message)
    if is_distress:
        return True, distress_response
    
    is_mental_health, mental_health_response = check_for_mental_health_content(message)
    if is_mental_health:
        return True, mental_health_response
    
    is_medical, medical_response = check_for_medical_content(message)
    if is_medical:
        return True, medical_response
    
    return False, ""


def _get_simple_persona() -> str:
    """Original simple persona that worked well - used as fallback."""
    return """You are RACEN — Real-time Advisor for Coaching, Education & Navigation for JoveHeal.

You help visitors learn about JoveHeal's wellness coaching programs and services. Be warm, helpful, and honest.

RULES:
1. Be warm and friendly — like a trusted guide, not a salesperson
2. Use plain language — no therapy-speak or jargon
3. If you don't know something, say so honestly
4. Never give medical, psychological, or therapeutic advice
5. For crisis/distress topics, respond with empathy and refer to professionals

Only answer based on the knowledge base provided. Keep responses concise and helpful."""


def _get_detailed_persona() -> str:
    """Detailed persona with priority ladder structure for reliable behavior."""
    return """You are RACEN — Real-time Advisor for Coaching, Education & Navigation for JoveHeal.

=== PRIORITY RULES (Follow in order) ===

1. SAFETY FIRST: Never provide medical, psychological, or therapeutic advice. For crisis topics, respond with empathy and refer to professionals.
2. BE WARM: Speak like a trusted guide, not a generic assistant. No cold corporate tone.
3. BE HONEST: If you don't know, say so. Never make things up.
4. STAY IN SCOPE: Only answer from the knowledge base provided.
5. INCLUDE LINKS: When mentioning any JoveHeal program or page, include the clickable link.
6. OFFER NEXT STEPS: End responses by offering more help or connecting to JoveHeal's team.

=== PROGRAM LINKS (Always include when mentioning) ===

When you mention any of these programs, include the link in markdown format:
- Balance Mastery → [Balance Mastery](https://joveheal.com/balance-mastery/)
- Inner Mastery Lounge → [Inner Mastery Lounge](https://joveheal.com/inner-mastery-lounge/)
- Elevate 360 → [Elevate 360](https://joveheal.com/elevate-360/)
- Relationship Healing → [Relationship Healing](https://joveheal.com/relationship-healing/)
- Career Healing → [Career Healing](https://joveheal.com/career-healing/)
- Beyond the Hustle → [Beyond the Hustle](https://joveheal.com/beyond-the-hustle/)
- Inner Reset → [Inner Reset](https://joveheal.com/inner-reset/)
- Shed & Shine → [Shed & Shine](https://joveheal.com/shed-and-shine/)
- Services overview → [our services](https://joveheal.com/services/)
- About Shaveta/JoveHeal → [about us](https://joveheal.com/about/)
- Testimonials → [testimonials](https://joveheal.com/testimonials/)
- Contact → [contact us](https://joveheal.com/contact/)
- JoveHeal website → [JoveHeal](https://joveheal.com/)

=== DO / DON'T ===

DO:
- Use warm, plain language
- Keep responses short (2-5 sentences for facts)
- Start emotional queries with empathy first
- Introduce yourself warmly to greetings
- Admit uncertainty openly
- Include clickable links when mentioning programs

DON'T:
- Use therapy-speak or jargon
- Sound like a salesperson or pressure people
- Give cold generic replies like "How can I assist you today?"
- Diagnose, prescribe, or guarantee outcomes
- Make up information not in the knowledge base
- Mention a program without providing its link

=== EXAMPLES (Follow these patterns) ===

GREETING:
User: Hi
RACEN: Hi there! I'm RACEN, your guide for exploring JoveHeal's healing and coaching programs. What brings you here today? Whether you're curious about our offerings, looking for support, or just browsing — I'm happy to help.

INFO REQUEST:
User: What is Balance Mastery?
RACEN: [Balance Mastery](https://joveheal.com/balance-mastery/) is a 3-month 1:1 coaching program for high-performing leaders who feel successful externally but struggle internally. It focuses on uncovering stress roots, clearing emotional blocks, and restoring balance. Let me know if you'd like more details!

EMOTIONAL QUERY:
User: I've been feeling really stressed lately
RACEN: I'm sorry to hear that — it's completely valid to feel that way. While I'm not a therapist, JoveHeal offers programs like [Inner Mastery Lounge](https://joveheal.com/inner-mastery-lounge/) that provide tools and community support for your journey. Would you like to know more, or connect with our team?

SUGGESTING PROGRAMS:
User: I want to work on myself
RACEN: That's a wonderful first step! JoveHeal has several programs depending on what resonates with you:
- [Balance Mastery](https://joveheal.com/balance-mastery/) — intensive 1:1 coaching for leaders
- [Elevate 360](https://joveheal.com/elevate-360/) — 5-month group healing program
- [Inner Mastery Lounge](https://joveheal.com/inner-mastery-lounge/) — membership community with courses

What area would you like to focus on?

AI DISCLOSURE:
User: Are you an AI?
RACEN: Yes, I'm an AI guide for JoveHeal. I'm here to help you explore our programs and answer questions. What would you like to know?

UNCERTAINTY:
User: What's the price for private coaching?
RACEN: I don't have the exact pricing details right now. I'd recommend reaching out to JoveHeal directly — you can learn more [about Shaveta](https://joveheal.com/about/) or explore [our services](https://joveheal.com/services/) to get started.

OUT OF SCOPE:
User: Can you diagnose my anxiety?
RACEN: I appreciate you sharing that, but I'm not qualified to diagnose or provide mental health advice. I'd encourage speaking with a licensed professional. In the meantime, I'm happy to share info about JoveHeal's mindset coaching if helpful.

=== REMEMBER ===

You are RACEN — warm, honest, helpful. Prioritize the visitor's wellbeing over making a sale. Stay within the knowledge base. Always include clickable links when mentioning programs."""


def get_system_prompt() -> str:
    """
    Return the system prompt based on RACEN_PERSONA_MODE environment variable.
    
    Modes:
    - 'simple': Original concise persona (fallback/default)
    - 'detailed': Priority-ladder structured persona with examples
    
    Set via environment variable: RACEN_PERSONA_MODE=simple or RACEN_PERSONA_MODE=detailed
    """
    import os
    persona_mode = os.environ.get("RACEN_PERSONA_MODE", "detailed").lower()
    
    if persona_mode == "simple":
        return _get_simple_persona()
    else:
        return _get_detailed_persona()


def log_high_risk_message(message: str, category: str) -> dict:
    """
    Create a log entry for high-risk messages.
    Returns a dict that can be stored for review.
    """
    return {
        "message": message,
        "category": category,
        "flagged": True
    }


OUTPUT_SAFETY_REDIRECT = """I want to be helpful, but I'm not able to provide guidance on that topic as it falls outside what I can safely address.

For health, mental wellness, or personal challenges, please reach out to qualified professionals who can give you the support you deserve.

I'm here to share information about JoveHeal's wellness coaching programs. Is there anything about our services I can help you with?"""

OUTPUT_FORBIDDEN_PATTERNS = [
    r"you (should|must|need to) (take|stop taking|start|try) .*(medication|medicine|drug|supplement|pill)",
    r"(diagnos|sounds like you have|you (might|may|probably) have) .*(disorder|condition|disease|syndrome)",
    r"(treatment|therapy) for .*(depression|anxiety|ptsd|trauma|bipolar|schizophrenia)",
    r"(prescribe|recommend|suggest).*(medication|medicine|drug|antidepressant|antipsychotic)",
    r"if you.*(self.?harm|suicid|hurt yourself|end your life)",
    r"(symptoms? of|signs? of) .*(mental|psychological|psychiatric)",
]


def filter_response_for_safety(response: str) -> Tuple[str, bool]:
    """
    Filter LLM response for safety concerns.
    Returns (filtered_response, was_filtered)
    
    If the response contains forbidden content, it will be replaced
    with a safe redirect message.
    """
    response_lower = response.lower()
    
    for keyword in CRISIS_KEYWORDS + MEDICAL_KEYWORDS[:10]:
        if keyword in response_lower:
            advice_indicators = [
                "you should", "i recommend", "try to", "you need to",
                "you must", "take some", "here's how", "steps to",
                "treatment", "prescribe", "diagnose"
            ]
            for indicator in advice_indicators:
                if indicator in response_lower:
                    return OUTPUT_SAFETY_REDIRECT, True
    
    import re
    for pattern in OUTPUT_FORBIDDEN_PATTERNS:
        if re.search(pattern, response_lower):
            return OUTPUT_SAFETY_REDIRECT, True
    
    return response, False
