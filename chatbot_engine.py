"""
Chatbot Engine for JoveHeal

This module handles the core chatbot logic:
- Query processing with RAG
- Integration with OpenAI for response generation
- Context management for multi-turn conversations
"""

import os
from typing import List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from knowledge_base import search_knowledge_base, get_knowledge_base_stats
from safety_guardrails import apply_safety_filters, get_system_prompt, filter_response_for_safety, inject_program_links, append_contextual_links

_openai_client = None


def get_openai_client():
    """Lazy initialization of OpenAI client with validation."""
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
        print(f"Error initializing OpenAI client: {e}")
        return None


def is_openai_available() -> bool:
    """Check if OpenAI is properly configured."""
    return get_openai_client() is not None


def is_rate_limit_error(exception: BaseException) -> bool:
    """Check if the exception is a rate limit or quota violation error."""
    error_msg = str(exception)
    return (
        "429" in error_msg
        or "RATELIMIT_EXCEEDED" in error_msg
        or "quota" in error_msg.lower()
        or "rate limit" in error_msg.lower()
        or (hasattr(exception, "status_code") and exception.status_code == 429)
    )


def format_context_from_docs(documents: List[dict]) -> str:
    """Format retrieved documents into context for the LLM."""
    if not documents:
        return "No relevant information found in the knowledge base."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.get("source", "Unknown source")
        content = doc.get("content", "")
        context_parts.append(f"[Source {i}: {source}]\n{content}")
    
    return "\n\n---\n\n".join(context_parts)


def format_conversation_history(messages: List[dict]) -> List[dict]:
    """Format conversation history for the API call."""
    formatted = []
    for msg in messages[-6:]:
        if msg.get("role") in ["user", "assistant"]:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    return formatted


def generate_response(
    user_message: str,
    conversation_history: List[dict] = None,
    n_context_docs: int = 5
) -> dict:
    """
    Generate a response to the user's message using RAG.
    
    Args:
        user_message: The user's question
        conversation_history: Previous messages in the conversation
        n_context_docs: Number of context documents to retrieve
    
    Returns:
        dict with 'response', 'sources', and 'safety_triggered' keys
    """
    client = get_openai_client()
    if client is None:
        return {
            "response": "I'm temporarily unavailable. Please try again later or contact JoveHeal directly for assistance.",
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
    
    relevant_docs = search_knowledge_base(user_message, n_results=n_context_docs)
    context = format_context_from_docs(relevant_docs)
    
    system_prompt = get_system_prompt()
    
    augmented_system_prompt = f"""{system_prompt}

KNOWLEDGE BASE CONTEXT:
The following information is from JoveHeal's official website and documents. Use this to answer the user's question accurately:

{context}

IMPORTANT: Only use information from the context above. If the answer is not in the context, politely say you don't have that specific information and suggest they contact JoveHeal directly."""

    messages = [{"role": "system", "content": augmented_system_prompt}]
    
    if conversation_history:
        formatted_history = format_conversation_history(conversation_history)
        messages.extend(formatted_history)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_completion_tokens=1024
        )
        
        assistant_message = response.choices[0].message.content
        
        filtered_response, was_filtered = filter_response_for_safety(assistant_message)
        
        response_with_program_links = inject_program_links(filtered_response)
        
        final_response = append_contextual_links(user_message, response_with_program_links)
        
        sources = []
        for doc in relevant_docs:
            source = doc.get("source", "Unknown")
            if source not in sources:
                sources.append(source)
        
        return {
            "response": final_response,
            "sources": sources[:3],
            "safety_triggered": was_filtered,
            "safety_category": "output_filtered" if was_filtered else None
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating response: {error_msg}")
        
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            return {
                "response": "I'm experiencing high demand right now. Please try again in a moment.",
                "sources": [],
                "safety_triggered": False,
                "error": "rate_limit"
            }
        
        return {
            "response": "I apologize, but I'm having trouble processing your question right now. Please try again, or contact JoveHeal directly for assistance.",
            "sources": [],
            "safety_triggered": False,
            "error": str(e)
        }


def get_greeting_message() -> str:
    """Return the initial greeting message for new conversations."""
    return """Hi there, I'm RACEN — your real-time guide for healing and coaching at JoveHeal.

I'm here to help you explore our programs, understand our philosophy, and find what might be right for you.

Are you looking for:
- Program details (Balance Mastery+, Inner Mastery Lounge, Elevate 360)
- Healing philosophy and approach
- Membership and pricing info
- How to get started

What brings you here today?"""


def check_knowledge_base_status() -> dict:
    """Check if the knowledge base is ready."""
    stats = get_knowledge_base_stats()
    return {
        "ready": stats["total_chunks"] > 0,
        "chunks": stats["total_chunks"],
        "last_updated": stats.get("last_scrape")
    }
