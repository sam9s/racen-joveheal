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
    "Healing Sessions": "https://joveheal.com/healing-sessions/",
    "Healing Circle": "https://joveheal.com/healing-circle/",
    "Meta-U": "https://joveheal.com/meta-u/",
    "Money and Abundance": "https://joveheal.com/money-abundance-manifestation/",
    "Services": "https://joveheal.com/services/",
    "About": "https://joveheal.com/about/",
    "Testimonials": "https://joveheal.com/testimonials/",
    "Contact": "https://joveheal.com/contact/",
    "Homepage": "https://joveheal.com/",
}

TOPIC_TO_PROGRAMS = {
    "career": ["Career Healing", "Beyond the Hustle"],
    "job": ["Career Healing", "Beyond the Hustle"],
    "work": ["Career Healing", "Beyond the Hustle"],
    "professional": ["Career Healing", "Balance Mastery"],
    "relationship": ["Relationship Healing"],
    "marriage": ["Relationship Healing"],
    "partner": ["Relationship Healing"],
    "divorce": ["Relationship Healing"],
    "family": ["Relationship Healing"],
    "burnout": ["Beyond the Hustle", "Inner Reset"],
    "exhausted": ["Beyond the Hustle", "Inner Reset"],
    "tired": ["Beyond the Hustle", "Inner Reset"],
    "overwhelmed": ["Beyond the Hustle", "Inner Reset"],
    "stress": ["Inner Reset", "Beyond the Hustle"],
    "anxiety": ["Inner Reset", "Balance Mastery"],
    "mindset": ["Balance Mastery", "Inner Mastery Lounge"],
    "coaching": ["Balance Mastery", "Services"],
    "healing": ["Healing Sessions", "Services"],
    "transformation": ["Balance Mastery", "Elevate 360"],
    "energy": ["Healing Sessions", "Balance Mastery"],
    "emotional": ["Inner Reset", "Beyond the Hustle"],
    "community": ["Inner Mastery Lounge", "Healing Circle"],
    "support": ["Inner Mastery Lounge", "Elevate 360"],
    "group": ["Elevate 360", "Inner Mastery Lounge"],
    "money": ["Money and Abundance"],
    "abundance": ["Money and Abundance"],
    "wealth": ["Money and Abundance"],
    "financial": ["Money and Abundance", "Career Healing"],
    "confidence": ["Shed & Shine", "Balance Mastery"],
    "self-worth": ["Shed & Shine", "Inner Reset"],
    "weight": ["Shed & Shine"],
    "body": ["Shed & Shine"],
}

WARM_CLOSING_SENTENCES = [
    "Feel free to explore more when you're ready:",
    "If you'd like to dive deeper, these might resonate with you:",
    "Here are some programs that align with what we discussed:",
]

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
5. OFFER NEXT STEPS: End responses by offering more help or connecting to JoveHeal's team.

=== DO / DON'T ===

DO:
- Use warm, plain language
- Keep responses short (2-5 sentences for facts)
- Start emotional queries with empathy first
- Introduce yourself warmly to greetings
- Admit uncertainty openly

DON'T:
- Use therapy-speak or jargon
- Sound like a salesperson or pressure people
- Give cold generic replies like "How can I assist you today?"
- Diagnose, prescribe, or guarantee outcomes
- Make up information not in the knowledge base

=== EXAMPLES (Follow these patterns) ===

GREETING:
User: Hi
RACEN: Hi there! I'm RACEN, your guide for exploring JoveHeal's healing and coaching programs. What brings you here today? Whether you're curious about our offerings, looking for support, or just browsing — I'm happy to help.

INFO REQUEST:
User: What is Balance Mastery?
RACEN: Balance Mastery is a 3-month 1:1 coaching program for high-performing leaders who feel successful externally but struggle internally. It focuses on uncovering stress roots, clearing emotional blocks, and restoring balance. Let me know if you'd like more details!

EMOTIONAL QUERY:
User: I've been feeling really stressed lately
RACEN: I'm sorry to hear that — it's completely valid to feel that way. While I'm not a therapist, JoveHeal offers programs like "Beyond the Hustle" that help uncover emotional roots of exhaustion. Would you like to know more, or connect with our team?

AI DISCLOSURE:
User: Are you an AI?
RACEN: Yes, I'm an AI guide for JoveHeal. I'm here to help you explore our programs and answer questions. What would you like to know?

UNCERTAINTY:
User: What's the price for private coaching?
RACEN: I don't have the exact pricing details right now. I'd recommend reaching out to JoveHeal directly — would you like me to share how to contact them?

OUT OF SCOPE:
User: Can you diagnose my anxiety?
RACEN: I appreciate you sharing that, but I'm not qualified to diagnose or provide mental health advice. I'd encourage speaking with a licensed professional. In the meantime, I'm happy to share info about JoveHeal's mindset coaching if helpful.

=== REMEMBER ===

You are RACEN — warm, honest, helpful. Prioritize the visitor's wellbeing over making a sale. Stay within the knowledge base."""


def inject_program_links(response: str) -> str:
    """
    Post-process LLM response to add clickable links to program mentions.
    This is deterministic and doesn't change the persona behavior.
    
    Converts mentions like "Balance Mastery" or "balance mastery" to "[Balance Mastery](https://joveheal.com/balance-mastery/)"
    Case-insensitive matching, only converts if not already a markdown link.
    """
    import re
    
    result = response
    
    for program_name, url in JOVEHEAL_PROGRAM_URLS.items():
        if program_name in ["Services", "About", "Testimonials", "Contact", "Homepage"]:
            continue
        
        pattern = rf'(?<!\[)({re.escape(program_name)})(?!\]|\()'
        
        match = re.search(pattern, result, re.IGNORECASE)
        if match:
            matched_text = match.group(1)
            markdown_link = f"[{program_name}]({url})"
            result = result[:match.start()] + markdown_link + result[match.end():]
    
    return result


def _response_has_urls(response: str) -> bool:
    """Check if the response already contains markdown URLs."""
    import re
    return bool(re.search(r'\[[^\]]+\]\([^)]+\)', response))


def _is_crisis_response(response: str) -> bool:
    """Check if this is a crisis/safety redirect response."""
    crisis_indicators = [
        "crisis hotline",
        "mental health professional",
        "licensed therapist",
        "988",
        "911",
        "emergency services",
        "professional support",
        "reach out to qualified professionals"
    ]
    response_lower = response.lower()
    return any(indicator in response_lower for indicator in crisis_indicators)


def _get_programs_for_query(query: str) -> list:
    """
    Analyze query keywords and return relevant programs (max 3, deduplicated).
    """
    query_lower = query.lower()
    suggested_programs = []
    seen = set()
    
    for keyword, programs in TOPIC_TO_PROGRAMS.items():
        if keyword in query_lower:
            for program in programs:
                if program not in seen and len(suggested_programs) < 3:
                    suggested_programs.append(program)
                    seen.add(program)
    
    return suggested_programs


def append_contextual_links(query: str, response: str) -> str:
    """
    Append contextual program links at the end of response if:
    1. Response has no URLs already (RACEN didn't mention specific programs)
    2. Query matches at least one topic keyword
    3. Not a crisis response
    
    Returns the response with optional warm closing and program links appended.
    """
    import random
    
    if _response_has_urls(response):
        return response
    
    if _is_crisis_response(response):
        return response
    
    programs = _get_programs_for_query(query)
    
    if not programs:
        return response
    
    warm_sentence = random.choice(WARM_CLOSING_SENTENCES)
    
    links = []
    for program in programs:
        if program in JOVEHEAL_PROGRAM_URLS:
            url = JOVEHEAL_PROGRAM_URLS[program]
            links.append(f"[{program}]({url})")
    
    if not links:
        return response
    
    closing_block = f"\n\n---\n\n*{warm_sentence}*\n" + " | ".join(links)
    
    return response + closing_block


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

SAFE_REDIRECT_PATTERNS = [
    r"(recommend|suggest|encourage|reach out to|consult|speak with|talk to|see|contact).{0,30}(professional|therapist|counselor|doctor|physician|psychiatrist|psychologist|licensed|qualified|mental health)",
    r"(professional|therapist|counselor|doctor|licensed|qualified).{0,20}(support|help|care|guidance|advice)",
    r"(don'?t|do not|cannot|can'?t|unable to|not able to|not equipped to).{0,30}(offer|provide).{0,30}(therapy|counseling|medical|treatment|diagnosis)",
    r"(we'?re not|i'?m not|joveheal is not|this is not).{0,30}(therapy|counseling|substitute|replacement)",
    r"(outside|beyond|not within).{0,20}(what i can|my scope|my expertise|what we offer)",
]

UNSAFE_ADVICE_PATTERNS = [
    r"(i recommend|you should|try|you need).{0,20}(therapy|counseling|treatment) for (your|the|this)",
    r"(start|begin|get|undergo|seek).{0,15}(therapy|treatment|counseling) (for|to help with)",
    r"(therapy|treatment|medication) (will|can|should|would).{0,15}(help|fix|cure|treat)",
    r"(you have|sounds like|appears to be|i think you have).{0,20}(depression|anxiety|disorder|condition)",
]


def _split_into_sentences(text: str) -> list:
    """Split text into sentences for sentence-scoped analysis."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def _sentence_has_protected_keyword(sentence: str) -> bool:
    """Check if a sentence contains a protected keyword."""
    sentence_lower = sentence.lower()
    protected_keywords = CRISIS_KEYWORDS + MEDICAL_KEYWORDS[:10]
    return any(kw in sentence_lower for kw in protected_keywords)


def _sentence_matches_safe_redirect(sentence: str) -> bool:
    """Check if a sentence matches safe redirect patterns (professional referral)."""
    import re
    sentence_lower = sentence.lower()
    return any(re.search(pattern, sentence_lower) for pattern in SAFE_REDIRECT_PATTERNS)


def _sentence_matches_unsafe_advice(sentence: str) -> bool:
    """Check if a sentence matches unsafe advice patterns (giving medical/therapy advice)."""
    import re
    sentence_lower = sentence.lower()
    return any(re.search(pattern, sentence_lower) for pattern in UNSAFE_ADVICE_PATTERNS)


def filter_response_for_safety(response: str) -> Tuple[str, bool]:
    """
    Filter LLM response for safety concerns using sentence-scoped analysis.
    Returns (filtered_response, was_filtered)
    
    Logic:
    1. Split response into sentences
    2. For each sentence with a protected keyword:
       - If it matches a SAFE_REDIRECT_PATTERN → ALLOW (professional referral)
       - If it matches an UNSAFE_ADVICE_PATTERN → BLOCK (giving advice)
    3. Check global OUTPUT_FORBIDDEN_PATTERNS as final catch
    """
    import re
    
    sentences = _split_into_sentences(response)
    
    for sentence in sentences:
        if _sentence_has_protected_keyword(sentence):
            if _sentence_matches_safe_redirect(sentence):
                continue
            if _sentence_matches_unsafe_advice(sentence):
                return OUTPUT_SAFETY_REDIRECT, True
    
    response_lower = response.lower()
    for pattern in OUTPUT_FORBIDDEN_PATTERNS:
        if re.search(pattern, response_lower):
            return OUTPUT_SAFETY_REDIRECT, True
    
    return response, False
