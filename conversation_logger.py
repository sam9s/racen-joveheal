"""
Conversation Logging Module for JoveHeal Chatbot

Stores minimal conversation logs for debugging and review:
- Timestamp
- User question
- Bot answer
- Optional: safety flags
"""

import json
import os
from datetime import datetime
from pathlib import Path


LOG_DIR = Path("logs")
CONVERSATION_LOG_FILE = LOG_DIR / "conversations.json"


def ensure_log_directory():
    """Ensure the logs directory exists."""
    LOG_DIR.mkdir(exist_ok=True)


def load_conversation_logs() -> list:
    """Load existing conversation logs from file."""
    ensure_log_directory()
    
    if CONVERSATION_LOG_FILE.exists():
        try:
            with open(CONVERSATION_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_conversation_logs(logs: list):
    """Save conversation logs to file."""
    ensure_log_directory()
    
    with open(CONVERSATION_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False, default=str)


def log_conversation(
    session_id: str,
    user_question: str,
    bot_answer: str,
    safety_flagged: bool = False,
    safety_category: str = None
) -> dict:
    """
    Log a single conversation exchange.
    
    Args:
        session_id: Unique identifier for the chat session
        user_question: The user's question
        bot_answer: The bot's response
        safety_flagged: Whether safety filters were triggered
        safety_category: Category of safety concern if flagged
    
    Returns:
        The logged entry dict
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_question": user_question,
        "bot_answer": bot_answer,
        "safety_flagged": safety_flagged
    }
    
    if safety_flagged and safety_category:
        entry["safety_category"] = safety_category
    
    logs = load_conversation_logs()
    logs.append(entry)
    
    if len(logs) > 10000:
        logs = logs[-10000:]
    
    save_conversation_logs(logs)
    
    return entry


def get_session_history(session_id: str) -> list:
    """Get all conversation logs for a specific session."""
    logs = load_conversation_logs()
    return [log for log in logs if log.get("session_id") == session_id]


def get_recent_logs(limit: int = 100) -> list:
    """Get the most recent conversation logs."""
    logs = load_conversation_logs()
    return logs[-limit:] if logs else []


def get_flagged_conversations() -> list:
    """Get all conversations that were flagged for safety concerns."""
    logs = load_conversation_logs()
    return [log for log in logs if log.get("safety_flagged", False)]


def get_conversation_stats() -> dict:
    """Get basic statistics about conversations."""
    logs = load_conversation_logs()
    
    if not logs:
        return {
            "total_conversations": 0,
            "unique_sessions": 0,
            "safety_flags": 0,
            "first_log": None,
            "last_log": None
        }
    
    unique_sessions = set(log.get("session_id") for log in logs)
    safety_flags = sum(1 for log in logs if log.get("safety_flagged", False))
    
    return {
        "total_conversations": len(logs),
        "unique_sessions": len(unique_sessions),
        "safety_flags": safety_flags,
        "first_log": logs[0].get("timestamp") if logs else None,
        "last_log": logs[-1].get("timestamp") if logs else None
    }


def clear_old_logs(days: int = 30):
    """Remove logs older than specified number of days."""
    logs = load_conversation_logs()
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    filtered_logs = []
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log.get("timestamp", "")).timestamp()
            if log_time > cutoff:
                filtered_logs.append(log)
        except (ValueError, TypeError):
            filtered_logs.append(log)
    
    save_conversation_logs(filtered_logs)
    return len(logs) - len(filtered_logs)
