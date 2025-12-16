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
    filter_response_for_safety
)
from emotional_patterns import (
    identify_emotional_patterns,
    identify_pillars,
    get_cross_pillar_awareness_context,
    build_enhanced_search_query
)

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
    
    should_redirect, redirect_response = apply_safety_filters(user_message)
    if should_redirect:
        return {
            "response": redirect_response,
            "sources": [],
            "safety_triggered": True,
            "safety_category": "safety_redirect"
        }
    
    contextual_query = build_contextual_search_query(user_message, conversation_history)
    relevant_docs = search_coaching_content(contextual_query, n_results=n_context_docs)
    context = format_coaching_context(relevant_docs)
    
    has_relevant_content = bool(relevant_docs) and context != "No specific coaching content found for this topic."
    
    system_prompt = get_somera_system_prompt()
    
    personalization = ""
    if user_name:
        personalization = f"\nThe user's name is {user_name}. Use their name naturally in your response."
    
    if has_relevant_content:
        augmented_prompt = f"""{system_prompt}
{personalization}

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
            "response": filtered_response,
            "sources": sources,
            "safety_triggered": was_filtered,
            "safety_category": "output_filtered" if was_filtered else None
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
    
    should_redirect, redirect_response = apply_safety_filters(user_message)
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
        
        yield {
            "type": "done",
            "sources": sources,
            "safety_triggered": was_filtered,
            "full_response": filtered_response if was_filtered else full_response
        }
        
    except Exception as e:
        print(f"Error in SOMERA stream: {e}")
        yield {
            "type": "error",
            "error": f"Error generating response: {str(e)}"
        }
