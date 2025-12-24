"""
SOMERA Engine - Empathetic Coaching Assistant

SOMERA (Supportive, Open-Minded, Empathetic, Reflective Advisor) uses Shweta's
coaching content from video transcripts and session recordings to provide
empathetic, coaching-style support.

Unlike Jovee (informational), SOMERA focuses on emotional support and coaching guidance.
"""

import os
from typing import List, Generator

from knowledge_base import search_coaching_content, search_coaching_content_enhanced
from safety_guardrails import (
    get_somera_system_prompt,
    apply_safety_filters,
    filter_response_for_safety,
    apply_llm_critic
)
from emotional_patterns import (
    identify_emotional_patterns,
    identify_pillars,
    get_cross_pillar_awareness_context,
    build_enhanced_search_query
)
from readiness_scoring import calculate_readiness_score, get_transition_context

_openai_client = None

GREETING_PATTERNS = [
    "hi", "hello", "hey", "hiya", "howdy", "greetings",
    "good morning", "good afternoon", "good evening", "good night",
    "what's up", "whats up", "sup", "yo",
    "how are you", "how r u", "how're you", "how do you do",
    "nice to meet you", "pleased to meet you",
    "namaste", "hola", "bonjour"
]


def is_greeting(message: str) -> bool:
    """Check if the message is a simple greeting that doesn't need coaching content."""
    msg_lower = message.lower().strip()
    msg_clean = ''.join(c for c in msg_lower if c.isalnum() or c.isspace())
    
    if len(msg_clean) > 50:
        return False
    
    for pattern in GREETING_PATTERNS:
        if msg_clean == pattern or msg_clean.startswith(pattern + " ") or msg_clean.endswith(" " + pattern):
            return True
        if pattern in msg_clean and len(msg_clean) < 30:
            return True
    
    return False


SOLUTION_REQUEST_PATTERNS = [
    "what should i do",
    "what can i do",
    "how can i fix",
    "any advice",
    "some advice",
    "give me advice",
    "give me some advice",
    "give me suggestions",
    "give me some suggestions",
    "give me tips",
    "give me some tips",
    "give me guidance",
    "what do you suggest",
    "can you suggest",
    "you can suggest",
    "you might suggest",
    "help me with this",
    "i need guidance",
    "what are my options",
    "guide me",
    "can you guide",
    "what would you recommend",
    "give me steps",
    "give me some steps",
    "those steps you were talking",
    "certain steps",
    "what steps",
    "any steps",
    "some steps",
    "steps you can",
    "steps i can",
    "steps i should",
    "pointers you can",
    "pointers i can",
    "certain pointers",
    "some pointers",
    "any pointers",
    "give me pointers",
    "you can assist",
    "can you assist",
    "something you can assist",
    "anything you can assist",
    "something you can help",
    "anything you can help",
    "interested in that",
    "i want to know how",
    "tell me how",
    "show me how",
    "from your knowledge",
    "from your own knowledge",
    "advice or suggestions",
    "suggestions or advice",
    "need help",
    "want help",
    "could you help",
    "can you help",
]


NEGATION_PREFIXES = [
    "don't ", "dont ", "do not ", "doesn't ", "doesnt ", "does not ",
    "can't ", "cant ", "cannot ", "won't ", "wont ", "will not ",
    "not ", "no ", "never ", "later ", "maybe later"
]

def is_solution_requested(message: str, conversation_history: List[dict] = None) -> bool:
    """
    Detect if the user is explicitly asking for solutions, steps, or guidance.
    Also checks if they've asked multiple times (indicating frustration with probing).
    
    Handles negation: "I don't need help" won't trigger solution mode.
    """
    msg_lower = message.lower()
    
    def pattern_is_negated(text: str, pattern: str) -> bool:
        """Check if the pattern is preceded by negation words."""
        idx = text.find(pattern)
        if idx == -1:
            return False
        prefix = text[:idx].split()[-3:] if idx > 0 else []
        prefix_text = " ".join(prefix) + " "
        for neg in NEGATION_PREFIXES:
            if neg in prefix_text:
                return True
        return False
    
    for pattern in SOLUTION_REQUEST_PATTERNS:
        if pattern in msg_lower and not pattern_is_negated(msg_lower, pattern):
            return True
    
    if conversation_history:
        solution_request_count = 0
        for msg in conversation_history[-6:]:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                for pattern in SOLUTION_REQUEST_PATTERNS:
                    if pattern in content and not pattern_is_negated(content, pattern):
                        solution_request_count += 1
                        break
        if solution_request_count >= 1:
            for pattern in SOLUTION_REQUEST_PATTERNS:
                if pattern in msg_lower and not pattern_is_negated(msg_lower, pattern):
                    return True
            if solution_request_count >= 2:
                return True
    
    return False


def count_conversation_turns(conversation_history: List[dict]) -> int:
    """Count the number of user-assistant exchange pairs."""
    user_messages = sum(1 for msg in conversation_history if msg.get("role") == "user")
    return user_messages


def get_openai_client():
    """Get OpenAI client singleton."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    
    if not api_key or not base_url:
        return None
    
    try:
        from openai import OpenAI
        _openai_client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        return _openai_client
    except Exception as e:
        print(f"Error initializing OpenAI client for SOMERA: {e}")
        return None


def format_coaching_context(documents: List[dict]) -> str:
    """Format retrieved coaching documents into context for SOMERA."""
    if not documents:
        return "No specific coaching content found for this topic."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.get("video_title", doc.get("source", "Coaching Content"))
        topic = doc.get("topic", "general")
        content = doc.get("content", "")
        context_parts.append(f"[From: {source} | Topic: {topic}]\n{content}")
    
    return "\n\n---\n\n".join(context_parts)


def format_conversation_history(messages: List[dict]) -> List[dict]:
    """Format conversation history for the API call.
    
    Keeps up to 40 messages to maintain context in longer coaching conversations.
    GPT-4o-mini supports ~128k tokens, so this is well within limits.
    """
    formatted = []
    for msg in messages[-40:]:
        if msg.get("role") in ["user", "assistant", "system"]:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    return formatted


def build_contextual_search_query(user_message: str, conversation_history: List[dict]) -> str:
    """
    Build a context-aware search query by combining current message with recent user context.
    
    This prevents source attribution errors in follow-up questions like:
    - User: "I'm unhappy at my job" → retrieves job content
    - User: "What steps should I take?" → without context, might retrieve "5 Steps" procrastination content
    
    With context: "What steps should I take?" + "unhappy at my job" → correctly retrieves job content
    """
    if not conversation_history:
        return user_message
    
    recent_user_messages = []
    for msg in conversation_history[-10:]:
        if msg.get("role") == "user":
            content = msg.get("content", "").strip()
            if content and len(content) > 10:
                recent_user_messages.append(content)
    
    if not recent_user_messages:
        return user_message
    
    context_summary = " ".join(recent_user_messages[-2:])
    contextual_query = f"{user_message} (context: {context_summary})"
    
    return contextual_query


def get_enhanced_coaching_context(user_message: str, conversation_history: List[dict], n_context_docs: int = 5) -> dict:
    """
    Get coaching context with emotional pattern awareness for cross-pillar retrieval.
    
    Returns:
        Dict with:
        - documents: Retrieved coaching documents
        - patterns: Identified emotional patterns
        - pillars: Identified life pillars
        - cross_pillar_context: Cross-pillar awareness context
    """
    all_text = user_message
    if conversation_history:
        for msg in conversation_history[-6:]:
            if msg.get("role") == "user":
                all_text += " " + msg.get("content", "")
    
    patterns = identify_emotional_patterns(all_text)
    pillars = identify_pillars(all_text)
    pattern_ids = [p.pattern_id for p in patterns]
    
    contextual_query = build_contextual_search_query(user_message, conversation_history)
    
    if pattern_ids:
        documents = search_coaching_content_enhanced(
            query=contextual_query,
            n_results=n_context_docs,
            emotional_patterns=pattern_ids,
            pillars=pillars
        )
    else:
        documents = search_coaching_content(contextual_query, n_results=n_context_docs)
    
    cross_pillar_context = ""
    if patterns and pillars:
        primary_pillar = pillars[0] if pillars else None
        cross_pillar_context = get_cross_pillar_awareness_context(patterns[:2], primary_pillar)
    
    return {
        "documents": documents,
        "patterns": patterns,
        "pattern_ids": pattern_ids,
        "pillars": pillars,
        "cross_pillar_context": cross_pillar_context
    }


def generate_somera_response(
    user_message: str,
    conversation_history: List[dict] = None,
    user_name: str = None,
    n_context_docs: int = 5
) -> dict:
    """
    Generate a SOMERA coaching response using RAG with coaching content.
    
    Args:
        user_message: The user's message
        conversation_history: Previous conversation messages
        user_name: Optional user name for personalization
        n_context_docs: Number of coaching documents to retrieve
    
    Returns:
        Dict with response, sources, and safety info
    """
    if conversation_history is None:
        conversation_history = []
    
    client = get_openai_client()
    if client is None:
        return {
            "response": "I'm temporarily unavailable. Please try again later or contact us at https://www.joveheal.com/contact for assistance.",
            "sources": [],
            "safety_triggered": False,
            "error": "openai_not_configured"
        }
    
    should_redirect, redirect_response = apply_safety_filters(user_message, is_somera=True)
    if should_redirect:
        return {
            "response": redirect_response,
            "sources": [],
            "safety_triggered": True,
            "safety_category": "safety_redirect"
        }
    
    enhanced_context = get_enhanced_coaching_context(user_message, conversation_history, n_context_docs)
    relevant_docs = enhanced_context["documents"]
    detected_patterns = enhanced_context["patterns"]
    detected_pillars = enhanced_context["pillars"]
    cross_pillar_context = enhanced_context["cross_pillar_context"]
    context = format_coaching_context(relevant_docs)
    
    has_relevant_content = bool(relevant_docs) and context != "No specific coaching content found for this topic."
    
    system_prompt = get_somera_system_prompt()
    
    personalization = ""
    if user_name:
        personalization = f"\nThe user's name is {user_name}. Use their name naturally in your response."
    
    cross_pillar_awareness = ""
    if detected_patterns and detected_pillars:
        pattern_names = [p.name for p in detected_patterns[:2]]
        cross_pillar_awareness = f"""

=== CROSS-PILLAR AWARENESS ===
You've detected these emotional patterns: {', '.join(pattern_names)}
The user is discussing: {', '.join(detected_pillars)}

IMPORTANT: These patterns often show up across ALL life areas (career, relationships, wellness).
When appropriate, gently probe if they notice similar feelings in other areas:
- "I'm curious - do you notice this feeling showing up in other parts of your life too?"
- "Sometimes what we feel at work can be connected to other areas. How is this affecting you elsewhere?"

{cross_pillar_context}"""
    
    solution_mode = is_solution_requested(user_message, conversation_history)
    conversation_turns = count_conversation_turns(conversation_history)
    
    readiness_result = calculate_readiness_score(user_message, conversation_history)
    readiness_context = get_transition_context(readiness_result)
    
    print(f"[SOMERA Debug - Non-stream] Message: '{user_message[:50]}...', Solution mode: {solution_mode}, Turns: {conversation_turns}")
    print(f"[SOMERA Debug - Non-stream] Readiness: {readiness_result['total_score']:.1%} ({readiness_result['recommendation']})")
    
    readiness_guide = readiness_result["recommendation"] == "guide"
    readiness_transition = readiness_result["recommendation"] == "transition"
    depth_guide = conversation_turns >= 5
    
    solution_mode_directive = ""
    
    if solution_mode:
        print(f"[SOMERA Debug - Non-stream] EXPLICIT SOLUTION MODE ACTIVATED!")
        solution_mode_directive = """

=== ⚠️ SOLUTION MODE ACTIVATED - CRITICAL INSTRUCTION ===

The user has EXPLICITLY requested guidance, steps, or solutions. You MUST now PROVIDE ANSWERS, NOT QUESTIONS.

**MANDATORY REQUIREMENTS - FAILURE TO FOLLOW WILL BE CONSIDERED A BUG:**

1. **DO NOT ASK ANY QUESTIONS** - Not even "Would you be open to..." or "What do you think might help?" or any variation. The user has ALREADY asked for help.

2. **PROVIDE 2-3 CONCRETE INSIGHTS NOW** from the coaching content:
   - Start with a brief acknowledgment (1 sentence MAX)
   - Then immediately provide actionable perspectives or steps
   - Each insight should be specific and grounded in the coaching wisdom

3. **FORMAT YOUR RESPONSE LIKE THIS:**
   "Thank you for sharing that with me. Based on what you've described, here are some perspectives that might resonate:

   First, [specific insight from coaching content about their situation]...

   Second, [another concrete perspective or reframe]...

   If you'd like to go deeper with these insights, working with Shweta directly can help you..."

4. **BANNED PHRASES - DO NOT USE:**
   - "Would you be open to..."
   - "Would it help if I shared..."
   - "What do you think..."
   - "How does that resonate..."
   - Any question asking for their input before giving guidance

5. **YOUR ROLE NOW:** You are a coach DELIVERING wisdom, not gathering more information. Give them something valuable to take away RIGHT NOW.
"""
    elif readiness_guide or depth_guide:
        print(f"[SOMERA Debug - Non-stream] READINESS-BASED GUIDANCE MODE")
        solution_mode_directive = f"""

=== GUIDANCE MODE - GENTLE TRANSITION ===

Based on conversation signals, the user may be ready to receive perspective and insights.
Readiness score: {readiness_result['total_score']:.0%}

**BALANCED APPROACH:**

1. **Lead with empathy** - Acknowledge their experience with 1-2 warm sentences

2. **Offer 1-2 perspectives** from the coaching content:
   - Present insights as invitations, not prescriptions
   - "One thing that often helps in situations like this..."
   - "Something worth considering..."

3. **Leave space for their response** - End with a gentle check-in:
   - "Does any of this resonate with you?"
   - "Would you like to explore this further?"

4. **Stay curious** - You may still ask ONE thoughtful follow-up question if it serves their exploration

Balance: 50% acknowledgment/empathy, 50% gentle guidance.
"""
    elif readiness_transition and readiness_context:
        print(f"[SOMERA Debug - Non-stream] READINESS TRANSITION MODE")
        solution_mode_directive = readiness_context
    
    if has_relevant_content:
        augmented_prompt = f"""{system_prompt}
{personalization}
{cross_pillar_awareness}
{solution_mode_directive}

=== SHWETA'S COACHING WISDOM ===
The following is from Shweta's actual coaching content. You MUST base your response on these insights:

{context}

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY share advice, frameworks, or steps that come from the coaching content above
2. If the user asks for "steps" or "advice", draw ONLY from what's in the coaching content
3. If the content doesn't cover what the user is asking, say: "Based on the coaching content I have, I don't have specific guidance on that topic. Would you like to explore what we discussed earlier, or connect with our team for more personalized support?"
4. DO NOT invent coaching steps, frameworks, or advice that aren't in the content above
5. You may use warm, empathetic language around the content, but the core advice must come from Shweta's teachings
6. Weave the teachings naturally - don't quote sources directly, but stay true to the actual content"""
    else:
        augmented_prompt = f"""{system_prompt}
{personalization}
{cross_pillar_awareness}
{solution_mode_directive}

NOTE: I don't have specific coaching content for this topic in my knowledge base. Respond warmly and empathetically, but be honest that you don't have specific coaching guidance. Offer to help them explore related topics or connect with the JoveHeal team."""

    messages = [{"role": "system", "content": augmented_prompt}]
    
    if conversation_history:
        formatted_history = format_conversation_history(conversation_history)
        messages.extend(formatted_history)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_completion_tokens=1024
        )
        
        assistant_message = response.choices[0].message.content
        
        filtered_response, was_filtered = filter_response_for_safety(assistant_message)
        
        critic_response, was_critic_corrected = apply_llm_critic(filtered_response)
        final_response = critic_response
        
        sources = []
        seen_videos = set()
        for doc in relevant_docs[:3]:
            video_title = doc.get("video_title", doc.get("source", "Unknown"))
            if video_title not in seen_videos:
                seen_videos.add(video_title)
                sources.append({
                    "source": video_title,
                    "topic": doc.get("topic", "general"),
                    "youtube_url": doc.get("youtube_url")
                })
        
        return {
            "response": final_response,
            "sources": sources,
            "safety_triggered": was_filtered or was_critic_corrected,
            "safety_category": "output_filtered" if was_filtered else ("critic_corrected" if was_critic_corrected else None)
        }
        
    except Exception as e:
        print(f"Error generating SOMERA response: {e}")
        return {
            "response": "I'm having a moment of difficulty. Please try again, or reach out to us at https://www.joveheal.com/contact.",
            "sources": [],
            "safety_triggered": False,
            "error": str(e)
        }


def generate_somera_response_stream(
    user_message: str,
    conversation_history: List[dict] = None,
    user_name: str = None,
    n_context_docs: int = 5
) -> Generator[dict, None, None]:
    """
    Generate a streaming SOMERA coaching response.
    
    Yields chunks with type 'content' for text and 'done' when complete.
    """
    if conversation_history is None:
        conversation_history = []
    
    client = get_openai_client()
    if client is None:
        yield {
            "type": "error",
            "error": "SOMERA is temporarily unavailable. Please try again later."
        }
        return
    
    should_redirect, redirect_response = apply_safety_filters(user_message, is_somera=True)
    if should_redirect:
        yield {
            "type": "content",
            "content": redirect_response
        }
        yield {
            "type": "done",
            "sources": [],
            "safety_triggered": True,
            "full_response": redirect_response
        }
        return
    
    is_simple_greeting = is_greeting(user_message)
    
    if is_simple_greeting:
        relevant_docs = []
        context = ""
        has_relevant_content = False
        cross_pillar_context = ""
        detected_patterns = []
        detected_pillars = []
    else:
        enhanced_context = get_enhanced_coaching_context(user_message, conversation_history, n_context_docs)
        relevant_docs = enhanced_context["documents"]
        detected_patterns = enhanced_context["patterns"]
        detected_pillars = enhanced_context["pillars"]
        cross_pillar_context = enhanced_context["cross_pillar_context"]
        context = format_coaching_context(relevant_docs)
        has_relevant_content = bool(relevant_docs) and context != "No specific coaching content found for this topic."
    
    system_prompt = get_somera_system_prompt()
    
    personalization = ""
    if user_name:
        personalization = f"\nThe user's name is {user_name}. Use their name naturally in your response."
    
    cross_pillar_awareness = ""
    if detected_patterns and detected_pillars:
        pattern_names = [p.name for p in detected_patterns[:2]]
        cross_pillar_awareness = f"""

=== CROSS-PILLAR AWARENESS ===
You've detected these emotional patterns: {', '.join(pattern_names)}
The user is discussing: {', '.join(detected_pillars)}

IMPORTANT: These patterns often show up across ALL life areas (career, relationships, wellness).
When appropriate, gently probe if they notice similar feelings in other areas:
- "I'm curious - do you notice this feeling showing up in other parts of your life too?"
- "Sometimes what we feel at work can be connected to other areas. How is this affecting you elsewhere?"

{cross_pillar_context}"""
    
    solution_mode = is_solution_requested(user_message, conversation_history)
    conversation_turns = count_conversation_turns(conversation_history)
    
    readiness_result = calculate_readiness_score(user_message, conversation_history)
    readiness_context = get_transition_context(readiness_result)
    
    print(f"[SOMERA Debug - Stream] Message: '{user_message[:50]}...', Solution mode: {solution_mode}, Turns: {conversation_turns}")
    print(f"[SOMERA Debug - Stream] Readiness: {readiness_result['total_score']:.1%} ({readiness_result['recommendation']})")
    
    readiness_guide = readiness_result["recommendation"] == "guide"
    readiness_transition = readiness_result["recommendation"] == "transition"
    depth_guide = conversation_turns >= 5
    
    solution_mode_directive = ""
    
    if solution_mode:
        print(f"[SOMERA Debug - Stream] EXPLICIT SOLUTION MODE ACTIVATED!")
        solution_mode_directive = """

=== ⚠️ SOLUTION MODE ACTIVATED - CRITICAL INSTRUCTION ===

The user has EXPLICITLY requested guidance, steps, or solutions. You MUST now PROVIDE ANSWERS, NOT QUESTIONS.

**MANDATORY REQUIREMENTS - FAILURE TO FOLLOW WILL BE CONSIDERED A BUG:**

1. **DO NOT ASK ANY QUESTIONS** - Not even "Would you be open to..." or "What do you think might help?" or any variation. The user has ALREADY asked for help.

2. **PROVIDE 2-3 CONCRETE INSIGHTS NOW** from the coaching content:
   - Start with a brief acknowledgment (1 sentence MAX)
   - Then immediately provide actionable perspectives or steps
   - Each insight should be specific and grounded in the coaching wisdom

3. **FORMAT YOUR RESPONSE LIKE THIS:**
   "Thank you for sharing that with me. Based on what you've described, here are some perspectives that might resonate:

   First, [specific insight from coaching content about their situation]...

   Second, [another concrete perspective or reframe]...

   If you'd like to go deeper with these insights, working with Shweta directly can help you..."

4. **BANNED PHRASES - DO NOT USE:**
   - "Would you be open to..."
   - "Would it help if I shared..."
   - "What do you think..."
   - "How does that resonate..."
   - Any question asking for their input before giving guidance

5. **YOUR ROLE NOW:** You are a coach DELIVERING wisdom, not gathering more information. Give them something valuable to take away RIGHT NOW.
"""
    elif readiness_guide or depth_guide:
        print(f"[SOMERA Debug - Stream] READINESS-BASED GUIDANCE MODE")
        solution_mode_directive = f"""

=== GUIDANCE MODE - GENTLE TRANSITION ===

Based on conversation signals, the user may be ready to receive perspective and insights.
Readiness score: {readiness_result['total_score']:.0%}

**BALANCED APPROACH:**

1. **Lead with empathy** - Acknowledge their experience with 1-2 warm sentences

2. **Offer 1-2 perspectives** from the coaching content:
   - Present insights as invitations, not prescriptions
   - "One thing that often helps in situations like this..."
   - "Something worth considering..."

3. **Leave space for their response** - End with a gentle check-in:
   - "Does any of this resonate with you?"
   - "Would you like to explore this further?"

4. **Stay curious** - You may still ask ONE thoughtful follow-up question if it serves their exploration

Balance: 50% acknowledgment/empathy, 50% gentle guidance.
"""
    elif readiness_transition and readiness_context:
        print(f"[SOMERA Debug - Stream] READINESS TRANSITION MODE")
        solution_mode_directive = readiness_context
    
    if is_simple_greeting:
        augmented_prompt = f"""{system_prompt}
{personalization}

The user is greeting you. Respond with THIS exact greeting:

"Hello there, beautiful soul ❤️. I'm Somera. Let me know how I can support you today — whether you have a question, something on your mind, or just need someone to talk with 😊."

This is the standard welcome message - use it exactly as written with the emojis.

Do NOT provide any coaching advice yet - just welcome them warmly."""
    elif has_relevant_content:
        augmented_prompt = f"""{system_prompt}
{personalization}
{cross_pillar_awareness}
{solution_mode_directive}

=== SHWETA'S COACHING WISDOM ===
The following is from Shweta's actual coaching content. You MUST base your response on these insights:

{context}

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY share advice, frameworks, or steps that come from the coaching content above
2. If the user asks for "steps" or "advice", draw ONLY from what's in the coaching content
3. If the content doesn't cover what the user is asking, say: "Based on the coaching content I have, I don't have specific guidance on that topic. Would you like to explore what we discussed earlier, or connect with our team for more personalized support?"
4. DO NOT invent coaching steps, frameworks, or advice that aren't in the content above
5. You may use warm, empathetic language around the content, but the core advice must come from Shweta's teachings
6. Weave the teachings naturally - don't quote sources directly, but stay true to the actual content"""
    else:
        augmented_prompt = f"""{system_prompt}
{personalization}
{cross_pillar_awareness}
{solution_mode_directive}

NOTE: I don't have specific coaching content for this topic in my knowledge base. Respond warmly and empathetically, but be honest that you don't have specific coaching guidance. Offer to help them explore related topics or connect with the JoveHeal team."""

    messages = [{"role": "system", "content": augmented_prompt}]
    
    if conversation_history:
        formatted_history = format_conversation_history(conversation_history)
        messages.extend(formatted_history)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_completion_tokens=1024,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield {
                    "type": "content",
                    "content": content
                }
        
        filtered_response, was_filtered = filter_response_for_safety(full_response)
        
        critic_response, was_critic_corrected = apply_llm_critic(filtered_response)
        final_response = critic_response
        
        sources = []
        if not is_simple_greeting:
            seen_videos = set()
            for doc in relevant_docs[:3]:
                video_title = doc.get("video_title", doc.get("source", "Unknown"))
                if video_title not in seen_videos:
                    seen_videos.add(video_title)
                    sources.append({
                        "source": video_title,
                        "topic": doc.get("topic", "general"),
                        "youtube_url": doc.get("youtube_url")
                    })
        
        if was_filtered or was_critic_corrected:
            yield {
                "type": "correction",
                "corrected_response": final_response
            }
        
        yield {
            "type": "done",
            "sources": sources,
            "safety_triggered": was_filtered or was_critic_corrected,
            "full_response": final_response
        }
        
    except Exception as e:
        print(f"Error in SOMERA stream: {e}")
        yield {
            "type": "error",
            "error": f"Error generating response: {str(e)}"
        }
