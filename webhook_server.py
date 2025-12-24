"""
Webhook Server for Multi-Channel Messaging

Flask-based API server handling:
- WhatsApp webhooks (via Twilio)
- Instagram webhooks (via Meta Graph API)
- Direct API access for custom integrations
- React frontend API endpoints
"""

import os
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from channel_handlers import (
    whatsapp_handler,
    instagram_handler,
    process_channel_message,
    get_channel_status
)
from chatbot_engine import generate_response, generate_response_stream, generate_conversation_summary, fix_typos_with_llm
from somera_engine import generate_somera_response, generate_somera_response_stream
from conversation_logger import log_feedback, log_conversation, ensure_session_exists
from database import get_or_create_user, get_user_conversation_history, get_conversation_summary, upsert_conversation_summary
from knowledge_base import initialize_knowledge_base, get_knowledge_base_stats

app = Flask(__name__)
CORS(app)

KNOWLEDGE_BASE_READY = False

def init_knowledge_base_on_startup():
    """Initialize knowledge base on startup if empty (for autoscale cold starts).
    
    FAIL FAST: If knowledge base cannot be initialized, exit with error.
    This prevents serving degraded traffic with missing vectors.
    """
    global KNOWLEDGE_BASE_READY
    try:
        stats = get_knowledge_base_stats()
        if stats["total_chunks"] == 0:
            print("[Startup] Knowledge base is empty, rebuilding from website...")
            initialize_knowledge_base(force_refresh=False, enable_web_scrape=True)
            stats = get_knowledge_base_stats()
            if stats["total_chunks"] == 0:
                print("[CRITICAL] Knowledge base rebuild failed - no chunks available!")
                print("[CRITICAL] Exiting to prevent serving degraded traffic.")
                import sys
                sys.exit(1)
            print(f"[Startup] Knowledge base rebuilt with {stats['total_chunks']} chunks")
        else:
            print(f"[Startup] Knowledge base ready with {stats['total_chunks']} chunks")
        KNOWLEDGE_BASE_READY = True
    except Exception as e:
        print(f"[CRITICAL] Failed to initialize knowledge base: {e}")
        print("[CRITICAL] Exiting to prevent serving degraded traffic.")
        import sys
        sys.exit(1)

init_knowledge_base_on_startup()

conversation_histories = {}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint.
    
    Returns unhealthy if knowledge base is not ready.
    """
    if not KNOWLEDGE_BASE_READY:
        return jsonify({
            "status": "unhealthy",
            "service": "R.A.C.E.N API Server",
            "reason": "Knowledge base not initialized"
        }), 503
    return jsonify({"status": "healthy", "service": "R.A.C.E.N API Server"})


@app.route("/api/channels/status", methods=["GET"])
def channel_status():
    """Get configuration status of all messaging channels."""
    return jsonify(get_channel_status())


def get_canonical_webhook_url(endpoint: str) -> str:
    """Get the canonical webhook URL for signature validation.
    
    Priority:
    1. WEBHOOK_BASE_URL - Trusted, explicitly configured base URL (most secure)
    2. REPLIT_DEV_DOMAIN - Replit's trusted domain environment variable
    3. Fallback error - Requires explicit configuration for security
    """
    webhook_base = os.environ.get("WEBHOOK_BASE_URL")
    if webhook_base:
        return f"{webhook_base.rstrip('/')}/{endpoint}"
    
    replit_domain = os.environ.get("REPLIT_DEV_DOMAIN")
    if replit_domain:
        return f"https://{replit_domain}/{endpoint}"
    
    return None


@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages via Twilio."""
    if not whatsapp_handler.is_configured():
        return "WhatsApp not configured", 503
    
    signature = request.headers.get("X-Twilio-Signature", "")
    
    if not signature:
        print(f"WhatsApp webhook: Rejected request - missing X-Twilio-Signature header. Remote: {request.remote_addr}")
        return "Missing signature", 403
    
    canonical_url = get_canonical_webhook_url("webhook/whatsapp")
    if not canonical_url:
        print("WhatsApp webhook: WEBHOOK_BASE_URL or REPLIT_DEV_DOMAIN must be set for signature validation")
        return "Server configuration error", 500
    
    if not whatsapp_handler.validate_request(signature, canonical_url, request.form.to_dict()):
        print(f"WhatsApp webhook: Rejected request - invalid signature. URL: {canonical_url}, Remote: {request.remote_addr}")
        return "Invalid signature", 403
    
    twiml_response = whatsapp_handler.handle_webhook(request.form.to_dict())
    
    return twiml_response, 200, {"Content-Type": "application/xml"}


@app.route("/webhook/instagram", methods=["GET"])
def instagram_verify():
    """Handle Instagram webhook verification."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    success, response = instagram_handler.verify_webhook(mode, token, challenge)
    
    if success:
        return response, 200
    return response, 403


@app.route("/webhook/instagram", methods=["POST"])
def instagram_webhook():
    """Handle incoming Instagram messages."""
    if not instagram_handler.is_configured():
        return jsonify({"error": "Instagram not configured"}), 503
    
    data = request.get_json()
    
    result = instagram_handler.handle_webhook(data)
    
    return jsonify(result), 200


def validate_internal_api_key():
    """Validate the internal API key from trusted Next.js server."""
    expected_key = os.environ.get("INTERNAL_API_KEY")
    if not expected_key:
        return False
    provided_key = request.headers.get("X-Internal-Api-Key", "")
    return provided_key == expected_key


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Direct API endpoint for chat integration - used by React frontend."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get("message")
    session_id = data.get("session_id", "anonymous")
    conversation_history = data.get("conversation_history", [])
    
    is_trusted_request = validate_internal_api_key()
    verified_user = data.get("verified_user") if is_trusted_request else None
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    original_message = message
    message = fix_typos_with_llm(message)
    
    user_id = None
    is_returning_user = False
    user_name = None
    
    if verified_user and session_id.startswith("user_"):
        email = verified_user.get("email")
        name = verified_user.get("name")
        image = verified_user.get("image")
        
        if email:
            user_data, created = get_or_create_user(
                channel="google",
                external_id=email,
                email=email,
                display_name=name,
                profile_image=image
            )
            if user_data:
                user_id = user_data['id']
                user_name = name.split()[0] if name else None
                is_returning_user = not created and session_id not in conversation_histories
    
    ensure_session_exists(session_id, channel="web", user_id=user_id)
    
    last_topic_summary = None
    stored_summary = None
    
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
        
        if is_returning_user and user_id:
            stored_summary = get_conversation_summary(user_id)
            
            past_history = get_user_conversation_history(user_id, limit=50)
            if past_history:
                for conv in past_history:
                    conversation_histories[session_id].append({"role": "user", "content": conv['question']})
                    conversation_histories[session_id].append({"role": "assistant", "content": conv['answer']})
            
            if stored_summary:
                summary_parts = []
                if stored_summary.get('emotional_themes'):
                    summary_parts.append(f"emotional issues: {stored_summary['emotional_themes']}")
                if stored_summary.get('recommended_programs'):
                    summary_parts.append(f"programs suggested: {stored_summary['recommended_programs']}")
                if stored_summary.get('last_topics'):
                    summary_parts.append(f"topic: {stored_summary['last_topics']}")
                last_topic_summary = " | ".join(summary_parts) if summary_parts else None
                
                if last_topic_summary:
                    conversation_histories[session_id] = conversation_histories[session_id][-4:]
    
    if conversation_history and not conversation_histories[session_id]:
        conversation_histories[session_id] = conversation_history
    
    result = generate_response(
        message, 
        conversation_histories[session_id],
        user_name=user_name,
        is_returning_user=is_returning_user,
        last_topic_summary=last_topic_summary
    )
    
    response_text = result.get("response", "")
    
    log_conversation(
        session_id=session_id,
        user_question=message,
        bot_answer=response_text,
        safety_flagged=result.get("safety_triggered", False),
        safety_category=result.get("safety_category"),
        sources=result.get("sources", []),
        channel="web"
    )
    
    conversation_histories[session_id].append({"role": "user", "content": message})
    conversation_histories[session_id].append({"role": "assistant", "content": response_text})
    
    if len(conversation_histories[session_id]) > 100:
        conversation_histories[session_id] = conversation_histories[session_id][-100:]
    
    if user_id and len(conversation_histories[session_id]) >= 4:
        try:
            summary = generate_conversation_summary(conversation_histories[session_id])
            if summary:
                upsert_conversation_summary(
                    user_id=user_id,
                    emotional_themes=summary.get('emotional_themes'),
                    recommended_programs=summary.get('recommended_programs'),
                    last_topics=summary.get('last_topics'),
                    conversation_status=summary.get('conversation_status')
                )
        except Exception as e:
            print(f"Error updating conversation summary: {e}")
    
    return jsonify({
        "response": result.get("response", "I apologize, but I encountered an issue. Please try again."),
        "sources": result.get("sources", []),
        "safety_triggered": result.get("safety_triggered", False),
        "session_id": session_id,
        "user_id": user_id,
        "is_returning_user": is_returning_user
    })


@app.route("/api/chat/stream", methods=["POST"])
def api_chat_stream():
    """Streaming chat endpoint using Server-Sent Events."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get("message")
    session_id = data.get("session_id", "anonymous")
    conversation_history = data.get("conversation_history", [])
    
    is_trusted_request = validate_internal_api_key()
    verified_user = data.get("verified_user") if is_trusted_request else None
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    original_message = message
    message = fix_typos_with_llm(message)
    
    user_id = None
    is_returning_user = False
    user_name = None
    
    if verified_user and session_id.startswith("user_"):
        email = verified_user.get("email")
        name = verified_user.get("name")
        image = verified_user.get("image")
        
        if email:
            user_data, created = get_or_create_user(
                channel="google",
                external_id=email,
                email=email,
                display_name=name,
                profile_image=image
            )
            if user_data:
                user_id = user_data['id']
                user_name = name.split()[0] if name else None
                is_returning_user = not created and session_id not in conversation_histories
    
    ensure_session_exists(session_id, channel="web", user_id=user_id)
    
    last_topic_summary = None
    stored_summary = None
    
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
        
        if is_returning_user and user_id:
            stored_summary = get_conversation_summary(user_id)
            
            past_history = get_user_conversation_history(user_id, limit=50)
            if past_history:
                for conv in past_history:
                    conversation_histories[session_id].append({"role": "user", "content": conv['question']})
                    conversation_histories[session_id].append({"role": "assistant", "content": conv['answer']})
            
            if stored_summary:
                summary_parts = []
                if stored_summary.get('emotional_themes'):
                    summary_parts.append(f"emotional issues: {stored_summary['emotional_themes']}")
                if stored_summary.get('recommended_programs'):
                    summary_parts.append(f"programs suggested: {stored_summary['recommended_programs']}")
                if stored_summary.get('last_topics'):
                    summary_parts.append(f"topic: {stored_summary['last_topics']}")
                last_topic_summary = " | ".join(summary_parts) if summary_parts else None
                
                if last_topic_summary:
                    conversation_histories[session_id] = conversation_histories[session_id][-4:]
    
    if conversation_history and not conversation_histories[session_id]:
        conversation_histories[session_id] = conversation_history
    
    def generate():
        full_response = ""
        sources = []
        safety_triggered = False
        
        for chunk in generate_response_stream(
            message, 
            conversation_histories[session_id],
            user_name=user_name,
            is_returning_user=is_returning_user,
            last_topic_summary=last_topic_summary
        ):
            if chunk["type"] == "content":
                full_response += chunk["content"]
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk["type"] == "done":
                sources = chunk.get("sources", [])
                safety_triggered = chunk.get("safety_triggered", False)
                full_response = chunk.get("full_response", full_response)
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk["type"] == "error":
                yield f"data: {json.dumps(chunk)}\n\n"
                return
        
        log_conversation(
            session_id=session_id,
            user_question=message,
            bot_answer=full_response,
            safety_flagged=safety_triggered,
            sources=sources,
            channel="web"
        )
        
        conversation_histories[session_id].append({"role": "user", "content": message})
        conversation_histories[session_id].append({"role": "assistant", "content": full_response})
        
        if len(conversation_histories[session_id]) > 100:
            conversation_histories[session_id] = conversation_histories[session_id][-100:]
        
        if user_id and len(conversation_histories[session_id]) >= 4:
            try:
                summary = generate_conversation_summary(conversation_histories[session_id])
                if summary:
                    upsert_conversation_summary(
                        user_id=user_id,
                        emotional_themes=summary.get('emotional_themes'),
                        recommended_programs=summary.get('recommended_programs'),
                        last_topics=summary.get('last_topics'),
                        conversation_status=summary.get('conversation_status')
                    )
            except Exception as e:
                print(f"Error updating conversation summary: {e}")
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


# ============================================================================
# SOMERA ENDPOINTS - Empathetic Coaching Assistant
# ============================================================================

somera_conversation_histories = {}

@app.route("/api/somera", methods=["POST"])
def api_somera():
    """SOMERA coaching endpoint - empathetic responses using Shweta's coaching style."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get("message")
    session_id = data.get("session_id", "anonymous")
    user_name = data.get("user_name")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    message = fix_typos_with_llm(message)
    
    if session_id not in somera_conversation_histories:
        somera_conversation_histories[session_id] = []
    
    result = generate_somera_response(
        message, 
        somera_conversation_histories[session_id],
        user_name=user_name
    )
    
    answer = result.get("response", "I'm here to support you. Could you tell me more?")
    sources = result.get("sources", [])
    
    somera_conversation_histories[session_id].append({"role": "user", "content": message})
    somera_conversation_histories[session_id].append({"role": "assistant", "content": answer})
    
    if len(somera_conversation_histories[session_id]) > 50:
        somera_conversation_histories[session_id] = somera_conversation_histories[session_id][-50:]
    
    return jsonify({
        "response": answer,
        "sources": sources,
        "session_id": session_id
    })


@app.route("/api/somera/stream", methods=["POST"])
def api_somera_stream():
    """Streaming SOMERA coaching endpoint using Server-Sent Events."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get("message")
    session_id = data.get("session_id", "anonymous")
    user_name = data.get("user_name")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    message = fix_typos_with_llm(message)
    
    if session_id not in somera_conversation_histories:
        somera_conversation_histories[session_id] = []
    
    def generate():
        full_response = ""
        sources = []
        
        for chunk in generate_somera_response_stream(
            message, 
            somera_conversation_histories[session_id],
            user_name=user_name
        ):
            if chunk["type"] == "content":
                full_response += chunk["content"]
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk["type"] == "done":
                sources = chunk.get("sources", [])
                full_response = chunk.get("full_response", full_response)
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk["type"] == "error":
                yield f"data: {json.dumps(chunk)}\n\n"
        
        somera_conversation_histories[session_id].append({"role": "user", "content": message})
        somera_conversation_histories[session_id].append({"role": "assistant", "content": full_response})
        
        if len(somera_conversation_histories[session_id]) > 50:
            somera_conversation_histories[session_id] = somera_conversation_histories[session_id][-50:]
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route("/api/chat/manychat", methods=["POST"])
def api_chat_manychat():
    """ManyChat Dynamic Content endpoint for Instagram/Facebook integration."""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "version": "v2",
            "content": {
                "messages": [{"type": "text", "text": "Sorry, I couldn't process your request."}],
                "actions": [],
                "quick_replies": []
            }
        })
    
    message = data.get("message", "").strip()
    user_id = data.get("user_id", "anonymous")
    first_name = data.get("first_name", "")
    
    if not message:
        return jsonify({
            "version": "v2",
            "content": {
                "messages": [{"type": "text", "text": "Hi! I'm Jovee, your guide for JoveHeal's wellness programs. How can I help you today?"}],
                "actions": [],
                "quick_replies": []
            }
        })
    
    session_id = f"manychat_{user_id}"
    
    original_message = message
    message = fix_typos_with_llm(message)
    
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    
    ensure_session_exists(session_id, channel="instagram", user_id=None)
    
    try:
        result = generate_response(
            message, 
            conversation_histories[session_id],
            user_name=first_name if first_name else None,
            is_returning_user=len(conversation_histories[session_id]) > 0,
            last_topic_summary=None
        )
        
        answer = result.get("response", "I'm sorry, I couldn't generate a response.")
        sources = result.get("sources", [])
        safety_triggered = result.get("safety_triggered", False)
        
        conversation_histories[session_id].append({"role": "user", "content": message})
        conversation_histories[session_id].append({"role": "assistant", "content": answer})
        
        if len(conversation_histories[session_id]) > 20:
            conversation_histories[session_id] = conversation_histories[session_id][-20:]
        
        log_conversation(
            session_id=session_id,
            user_question=original_message,
            bot_answer=answer,
            sources=sources,
            safety_flagged=safety_triggered
        )
        
        return jsonify({
            "version": "v2",
            "content": {
                "messages": [{"type": "text", "text": answer}],
                "actions": [],
                "quick_replies": []
            }
        })
        
    except Exception as e:
        print(f"ManyChat endpoint error: {e}")
        return jsonify({
            "version": "v2",
            "content": {
                "messages": [{"type": "text", "text": "I'm having trouble right now. Please try again in a moment."}],
                "actions": [],
                "quick_replies": []
            }
        })


@app.route("/api/chat/reset", methods=["POST"])
def api_chat_reset():
    """Reset conversation for a session."""
    data = request.get_json()
    session_id = data.get("session_id", "anonymous")
    
    if session_id in conversation_histories:
        del conversation_histories[session_id]
    
    return jsonify({
        "status": "success",
        "message": "Conversation reset"
    })


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """Submit feedback for a response."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    session_id = data.get("session_id", "anonymous")
    message_id = data.get("message_id", "")
    feedback = data.get("feedback", "")
    comment = data.get("comment", "")
    
    if feedback not in ["up", "down"]:
        return jsonify({"error": "Invalid feedback value"}), 400
    
    is_positive = feedback == "up"
    
    try:
        log_feedback(
            session_id=session_id,
            is_positive=is_positive,
            comment=comment if comment else None
        )
        
        return jsonify({
            "status": "success",
            "message": "Feedback recorded"
        })
    except Exception as e:
        print(f"Error logging feedback: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to record feedback"
        }), 500


# =============================================================================
# Admin Dashboard API Endpoints
# =============================================================================

from conversation_logger import (
    get_conversation_stats, get_analytics_by_date, get_feedback_summary,
    get_recent_logs, get_session_history
)
from database import ChatSession, Conversation, UserAccount, get_db_session, is_database_available
from sqlalchemy import func, desc

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    """Get dashboard statistics."""
    if not validate_internal_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    range_param = request.args.get("range", "7d")
    
    days = 7
    if range_param == "24h":
        days = 1
    elif range_param == "30d":
        days = 30
    
    try:
        stats = get_conversation_stats()
        daily_data = get_analytics_by_date(days)
        feedback = get_feedback_summary()
        
        total_feedback = feedback.get("positive", 0) + feedback.get("negative", 0)
        satisfaction = 0
        if total_feedback > 0:
            satisfaction = round((feedback.get("positive", 0) / total_feedback) * 100)
        
        channel_dist = []
        if is_database_available():
            with get_db_session() as db:
                if db:
                    channels = db.query(
                        ChatSession.channel,
                        func.count(ChatSession.id).label('count')
                    ).group_by(ChatSession.channel).all()
                    channel_dist = [{"channel": c.channel or "web", "count": c.count} for c in channels]
        
        conversations_by_day = []
        for d in daily_data:
            date_str = d.get("date", "")
            if date_str:
                from datetime import datetime
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted = dt.strftime("%b %d")
                except:
                    formatted = date_str
                conversations_by_day.append({
                    "date": formatted,
                    "count": d.get("conversations", 0)
                })
        
        top_queries = []
        
        return jsonify({
            "totalConversations": stats.get("total_conversations", 0),
            "totalSessions": stats.get("unique_sessions", 0),
            "avgResponseTime": round((stats.get("avg_response_time_ms") or 0) / 1000, 1),
            "positiveRating": satisfaction,
            "conversationsByDay": conversations_by_day,
            "channelDistribution": channel_dist if channel_dist else [{"channel": "Widget", "count": stats.get("total_conversations", 0)}],
            "topQueries": top_queries
        })
    except Exception as e:
        print(f"Admin stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/conversations", methods=["GET"])
def admin_conversations():
    """Get list of chat sessions for the conversation viewer."""
    if not validate_internal_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    range_param = request.args.get("range", "7d")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    
    days = 7
    if range_param == "24h":
        days = 1
    elif range_param == "30d":
        days = 30
    
    if not is_database_available():
        return jsonify({"sessions": [], "total": 0})
    
    try:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with get_db_session() as db:
            if db is None:
                return jsonify({"sessions": [], "total": 0})
            
            total = db.query(func.count(ChatSession.id)).filter(
                ChatSession.created_at >= cutoff
            ).scalar() or 0
            
            sessions = db.query(ChatSession).filter(
                ChatSession.created_at >= cutoff
            ).order_by(desc(ChatSession.last_activity)).offset((page - 1) * limit).limit(limit).all()
            
            result = []
            for s in sessions:
                msg_count = db.query(func.count(Conversation.id)).filter(
                    Conversation.session_id == s.session_id
                ).scalar() or 0
                
                first_msg = db.query(Conversation.user_question).filter(
                    Conversation.session_id == s.session_id
                ).order_by(Conversation.timestamp).first()
                
                user_name = "Anonymous"
                user_email = None
                if s.user_id:
                    user = db.query(UserAccount).filter(UserAccount.id == s.user_id).first()
                    if user:
                        user_name = user.display_name or user.email or "User"
                        user_email = user.email
                
                result.append({
                    "sessionId": s.session_id,
                    "userName": user_name,
                    "userEmail": user_email,
                    "channel": s.channel or "web",
                    "messageCount": msg_count,
                    "firstMessage": first_msg[0][:100] + "..." if first_msg and len(first_msg[0]) > 100 else (first_msg[0] if first_msg else ""),
                    "createdAt": s.created_at.isoformat() if s.created_at else None,
                    "lastActivity": s.last_activity.isoformat() if s.last_activity else None
                })
            
            return jsonify({
                "sessions": result,
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": (total + limit - 1) // limit
            })
    except Exception as e:
        print(f"Admin conversations error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/conversations/<session_id>", methods=["GET"])
def admin_conversation_detail(session_id):
    """Get full conversation history for a specific session."""
    if not validate_internal_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    if not is_database_available():
        return jsonify({"messages": [], "session": None})
    
    try:
        with get_db_session() as db:
            if db is None:
                return jsonify({"messages": [], "session": None})
            
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                return jsonify({"error": "Session not found"}), 404
            
            user_name = "Anonymous"
            user_email = None
            if session.user_id:
                user = db.query(UserAccount).filter(UserAccount.id == session.user_id).first()
                if user:
                    user_name = user.display_name or user.email or "User"
                    user_email = user.email
            
            messages = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.timestamp).all()
            
            message_list = []
            for m in messages:
                message_list.append({
                    "id": m.id,
                    "userQuestion": m.user_question,
                    "botAnswer": m.bot_answer,
                    "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                    "safetyFlagged": m.safety_flagged,
                    "responseTimeMs": m.response_time_ms
                })
            
            return jsonify({
                "session": {
                    "sessionId": session.session_id,
                    "userName": user_name,
                    "userEmail": user_email,
                    "channel": session.channel or "web",
                    "createdAt": session.created_at.isoformat() if session.created_at else None,
                    "lastActivity": session.last_activity.isoformat() if session.last_activity else None
                },
                "messages": message_list
            })
    except Exception as e:
        print(f"Admin conversation detail error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/transcribe", methods=["POST"])
def transcribe_audio():
    """Transcribe audio/video file using OpenAI Whisper API."""
    import tempfile
    import subprocess
    import math
    from openai import OpenAI
    
    if not validate_internal_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    output_name = request.form.get('outputName', 'transcript')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "OpenAI API key not configured"}), 500
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, file.filename)
            file.save(input_path)
            
            video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            audio_path = os.path.join(temp_dir, "audio.mp3")
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vn", "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
                "-y", audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return jsonify({"error": f"Failed to extract audio: {result.stderr[:200]}"}), 500
            
            if not os.path.exists(audio_path):
                return jsonify({"error": "Failed to extract audio - output file not created"}), 500
            
            def get_audio_duration(path):
                try:
                    cmd = [
                        "ffprobe", "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        path
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    if result.returncode != 0:
                        print(f"FFprobe error: {result.stderr}")
                        return 0
                    return float(result.stdout.strip())
                except Exception as e:
                    print(f"Duration detection error: {e}")
                    return 0
            
            duration = get_audio_duration(audio_path)
            chunk_duration = 600
            num_chunks = max(1, math.ceil(duration / chunk_duration))
            
            if num_chunks == 1:
                chunks = [audio_path]
            else:
                chunks = []
                for i in range(num_chunks):
                    start_time = i * chunk_duration
                    chunk_path = os.path.join(temp_dir, f"chunk_{i:03d}.mp3")
                    cmd = [
                        "ffmpeg", "-i", audio_path,
                        "-ss", str(start_time),
                        "-t", str(chunk_duration),
                        "-acodec", "libmp3lame", "-ab", "64k", "-ar", "16000",
                        "-y", chunk_path
                    ]
                    chunk_result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if chunk_result.returncode != 0:
                        print(f"Chunk {i} ffmpeg error: {chunk_result.stderr}")
                    if os.path.exists(chunk_path):
                        chunks.append(chunk_path)
            
            client = OpenAI(api_key=api_key)
            all_transcripts = []
            
            for chunk_path in chunks:
                with open(chunk_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                    all_transcripts.append(transcript)
            
            full_transcript = "\n\n".join(all_transcripts)
            
            transcript_path = os.path.join("transcripts", f"{output_name}_transcript.txt")
            os.makedirs("transcripts", exist_ok=True)
            with open(transcript_path, "w") as f:
                f.write(full_transcript)
            
            return jsonify({
                "transcript": full_transcript,
                "duration_minutes": duration / 60,
                "chunks": len(chunks),
                "saved_to": transcript_path
            })
    
    except Exception as e:
        print(f"Transcription error: {e}")
        return jsonify({"error": str(e)}), 500


vapi_conversation_histories = {}


def validate_vapi_request() -> bool:
    """
    Validate that the request is from VAPI.
    
    Checks for VAPI secret in Authorization header or x-vapi-secret header.
    If VAPI_WEBHOOK_SECRET is not configured, allows all requests (dev mode).
    """
    vapi_secret = os.environ.get("VAPI_WEBHOOK_SECRET", "")
    
    if not vapi_secret:
        return True
    
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        if auth_header[7:] == vapi_secret:
            return True
    
    vapi_header = request.headers.get("x-vapi-secret", "")
    if vapi_header == vapi_secret:
        return True
    
    return False


@app.route("/api/vapi/webhook", methods=["POST"])
def vapi_webhook():
    """
    VAPI Voice AI Webhook Endpoint
    
    Handles incoming requests from VAPI for SOMERA Voice Assistant.
    Supports:
    - tool-calls: Custom function calls to get SOMERA coaching responses
    - conversation-update: Track conversation state
    - end-of-call-report: Log completed calls
    - Other events: Acknowledge without action
    
    Security: Validates VAPI_WEBHOOK_SECRET if configured.
    """
    if not validate_vapi_request():
        print(f"[VAPI] Rejected request - invalid or missing authentication")
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request format"}), 400
        
        message = data["message"]
        message_type = message.get("type", "")
        call_id = message.get("call", {}).get("id", "unknown")
        
        print(f"[VAPI] Received {message_type} for call {call_id}")
        
        if message_type == "tool-calls":
            return handle_vapi_tool_calls(message, call_id)
        
        elif message_type == "conversation-update":
            return handle_vapi_conversation_update(message, call_id)
        
        elif message_type == "end-of-call-report":
            return handle_vapi_end_of_call(message, call_id)
        
        elif message_type == "assistant-request":
            return handle_vapi_assistant_request(message, call_id)
        
        elif message_type == "status-update":
            status = message.get("status", "")
            print(f"[VAPI] Call {call_id} status: {status}")
            return jsonify({}), 200
        
        elif message_type == "transcript":
            transcript = message.get("transcript", "")
            role = message.get("role", "")
            print(f"[VAPI] Transcript ({role}): {transcript[:100]}...")
            return jsonify({}), 200
        
        else:
            print(f"[VAPI] Unhandled message type: {message_type}")
            return jsonify({}), 200
            
    except Exception as e:
        print(f"[VAPI] Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


def handle_vapi_tool_calls(message: dict, call_id: str):
    """
    Handle VAPI tool/function calls.
    
    When VAPI's LLM decides to call our custom tool (e.g., get_somera_response),
    this function processes the request and returns the SOMERA response.
    
    Uses response_type: "final" to make VAPI speak our response verbatim
    without LLM reformulation, ensuring guardrails are followed exactly.
    """
    tool_calls = message.get("toolCallList", [])
    tool_with_call_list = message.get("toolWithToolCallList", [])
    
    if not tool_calls and tool_with_call_list:
        tool_calls = []
        for item in tool_with_call_list:
            tool_call = item.get("toolCall", {})
            tool_call["name"] = item.get("name", tool_call.get("name", ""))
            tool_calls.append(tool_call)
    
    results = []
    
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id", "")
        tool_name = tool_call.get("name", "")
        params = tool_call.get("parameters", {})
        
        print(f"[VAPI] Tool call: {tool_name} with params: {params}")
        
        if tool_name == "get_somera_response":
            user_message = params.get("user_message", params.get("message", ""))
            
            if not user_message:
                results.append({
                    "toolCallId": tool_call_id,
                    "result": "I didn't catch that. Could you please repeat?"
                })
                continue
            
            history = vapi_conversation_histories.get(call_id, [])
            
            try:
                response_data = generate_somera_response(
                    user_message=user_message,
                    conversation_history=history
                )
                response_text = response_data.get("response", "I'm here to listen. Could you tell me more?")
                response_text = optimize_response_for_voice(response_text)
                
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": response_text})
                vapi_conversation_histories[call_id] = history[-20:]
                
                print(f"[VAPI] SOMERA response: {response_text[:100]}...")
                
                results.append({
                    "toolCallId": tool_call_id,
                    "result": response_text,
                    "message": response_text
                })
                
            except Exception as e:
                print(f"[VAPI] SOMERA error: {e}")
                results.append({
                    "toolCallId": tool_call_id,
                    "result": "I'm having a moment. Could you share that with me again?"
                })
        
        else:
            results.append({
                "toolCallId": tool_call_id,
                "result": f"Unknown tool: {tool_name}"
            })
    
    return jsonify({"results": results}), 200


def handle_vapi_conversation_update(message: dict, call_id: str):
    """Track conversation updates from VAPI."""
    messages = message.get("messagesOpenAIFormatted", [])
    if messages:
        vapi_conversation_histories[call_id] = messages[-20:]
        print(f"[VAPI] Updated conversation history for call {call_id}: {len(messages)} messages")
    return jsonify({}), 200


def handle_vapi_end_of_call(message: dict, call_id: str):
    """Handle end of call report - log and clean up."""
    ended_reason = message.get("endedReason", "unknown")
    artifact = message.get("artifact", {})
    transcript = artifact.get("transcript", "")
    duration = message.get("call", {}).get("duration", 0)
    
    print(f"[VAPI] Call {call_id} ended. Reason: {ended_reason}, Duration: {duration}s")
    print(f"[VAPI] Transcript preview: {transcript[:200]}...")
    
    if call_id in vapi_conversation_histories:
        del vapi_conversation_histories[call_id]
    
    return jsonify({}), 200


def handle_vapi_assistant_request(message: dict, call_id: str):
    """
    Handle dynamic assistant configuration request.
    
    This is called when VAPI needs to know which assistant to use.
    We return a transient assistant configuration with SOMERA's persona.
    """
    elevenlabs_voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "")
    
    webhook_base = os.environ.get("WEBHOOK_BASE_URL", "")
    if not webhook_base:
        replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
        if replit_domain:
            webhook_base = f"https://{replit_domain}"
    
    webhook_url = f"{webhook_base}/api/vapi/webhook"
    
    assistant_config = {
        "assistant": {
            "name": "SOMERA Voice",
            "firstMessage": "Hello, this is Somera. I'm here to listen and support you. What's on your mind today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": get_somera_voice_system_prompt()
                    }
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_somera_response",
                            "description": "Get a coaching response from SOMERA based on what the user shared. Call this for every user message to provide empathetic coaching.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_message": {
                                        "type": "string",
                                        "description": "What the user said"
                                    }
                                },
                                "required": ["user_message"]
                            }
                        },
                        "async": False,
                        "server": {
                            "url": webhook_url
                        }
                    }
                ]
            },
            "voice": {
                "provider": "11labs",
                "voiceId": elevenlabs_voice_id or "21m00Tcm4TlvDq8ikWAM"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en"
            },
            "server": {
                "url": webhook_url
            },
            "silenceTimeoutSeconds": 30,
            "responseDelaySeconds": 0.5,
            "endCallMessage": "Thank you for sharing with me today. Take care of yourself, and remember, you're not alone on this journey.",
            "endCallPhrases": ["goodbye", "bye", "thank you bye", "that's all", "end call"]
        }
    }
    
    print(f"[VAPI] Returning assistant config for call {call_id}")
    return jsonify(assistant_config), 200


def get_somera_voice_system_prompt() -> str:
    """Get the system prompt optimized for voice interactions."""
    return """You are SOMERA, Shweta's empathetic AI coaching assistant for JoveHeal, speaking with someone on a phone call.

YOUR VOICE PERSONA:
- Warm, calm, and genuinely caring
- Speak naturally as if in a real conversation
- Use short, conversational sentences (this is a phone call, not text)
- Pause naturally between thoughts
- Never sound robotic or scripted

COACHING APPROACH:
- Listen with empathy and without judgment
- Ask gentle, open-ended questions to help them explore their feelings
- Reflect back what you hear to show understanding
- Guide them toward their own insights - don't give direct advice
- Focus on the Three Pillars: Career, Relationships, and Wellness

VOICE CONVERSATION RULES:
- Keep responses under 3-4 sentences - this is a conversation, not a lecture
- Use natural filler words occasionally ("I see", "mmm", "that makes sense")
- If they share something heavy, pause and acknowledge before continuing
- Never say "as an AI" or break character
- For deep healing topics (chakra work, energy healing, etc.), warmly suggest booking a Discovery Call with Shweta

IMPORTANT:
- Use the get_somera_response tool for EVERY user message to get coaching context
- Speak the response naturally, as Shweta would
- If the connection seems lost, gently ask if they're still there"""


def optimize_response_for_voice(text: str) -> str:
    """
    Optimize text response for voice/TTS output.
    
    - Remove markdown formatting
    - Shorten for conversational flow
    - Remove URLs (can't speak them naturally)
    - Add natural pauses
    """
    import re
    
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    text = re.sub(r'https?://[^\s]+', '', text)
    
    text = re.sub(r'^\s*[-*•]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
    
    text = text.replace('💙', '').replace('❤️', '').replace('✨', '').replace('🌟', '')
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    sentences = text.split('. ')
    if len(sentences) > 4:
        text = '. '.join(sentences[:4]) + '.'
    
    return text


custom_llm_conversation_histories = {}
voice_call_turn_counts = {}


def save_voice_message_async(call_id: str, role: str, content: str, readiness_score: float = None, readiness_recommendation: str = None):
    """Save a voice message to the database in a background thread (non-blocking for latency)."""
    import threading
    
    def _save():
        try:
            import psycopg2
            database_url = os.environ.get("DATABASE_URL")
            if not database_url:
                return
            
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO voice_conversations (call_id, started_at)
                VALUES (%s, CURRENT_TIMESTAMP)
                ON CONFLICT (call_id) DO NOTHING
            """, (call_id,))
            
            if readiness_score is not None:
                cur.execute("""
                    INSERT INTO voice_messages (call_id, role, content, readiness_score, readiness_recommendation, created_at)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (call_id, role, content, readiness_score, readiness_recommendation))
            else:
                cur.execute("""
                    INSERT INTO voice_messages (call_id, role, content, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (call_id, role, content))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"[Voice DB Async] Error: {e}")
    
    thread = threading.Thread(target=_save, daemon=True)
    thread.start()


def save_voice_message_to_db(call_id: str, role: str, content: str, readiness_score: float = None, readiness_recommendation: str = None):
    """Save a voice conversation message to the database."""
    try:
        import psycopg2
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("[Voice DB] DATABASE_URL not found, skipping save")
            return
        
        turn_number = voice_call_turn_counts.get(call_id, 0)
        if role == "user":
            turn_number += 1
            voice_call_turn_counts[call_id] = turn_number
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO voice_messages (call_id, turn_number, role, content, readiness_score, readiness_recommendation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (call_id, turn_number, role, content, readiness_score, readiness_recommendation))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[Voice DB] Saved {role} message for call {call_id}, turn {turn_number}")
        
    except Exception as e:
        print(f"[Voice DB] Error saving message: {e}")


def save_voice_call_summary(call_id: str, total_turns: int, full_transcript: str):
    """Save a summary of the voice call to the database."""
    try:
        import psycopg2
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            return
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO voice_conversations (call_id, total_turns, full_transcript, ended_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (call_id) DO UPDATE SET
                total_turns = EXCLUDED.total_turns,
                full_transcript = EXCLUDED.full_transcript,
                ended_at = CURRENT_TIMESTAMP
        """, (call_id, total_turns, full_transcript))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[Voice DB] Saved call summary for {call_id}")
        
    except Exception as e:
        print(f"[Voice DB] Error saving call summary: {e}")


@app.route("/api/vapi/chat/completions", methods=["POST"])
def vapi_custom_llm():
    """
    VAPI Custom LLM Endpoint - OpenAI-compatible /chat/completions
    
    This endpoint REPLACES VAPI's LLM entirely. VAPI sends us:
    - Deepgram transcription in OpenAI message format
    - We process with SOMERA engine
    - Return response that VAPI speaks with ElevenLabs
    
    NO VAPI LLM INTERFERENCE - we have full control.
    """
    import time as timing_module
    request_start = timing_module.time()
    
    try:
        data = request.get_json()
        if data:
            print(f"[VAPI Custom LLM] Raw request keys: {list(data.keys())}")
        messages = data.get("messages", [])
        stream = data.get("stream", False)
        
        call_metadata = data.get("call", {})
        call_id = call_metadata.get("id", "custom-llm-" + str(hash(str(messages)))[:8])
        
        print(f"[VAPI Custom LLM] Received request for call {call_id}, stream={stream}")
        
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        should_end_call = False
        
        if not user_message:
            response_text = "Hello! I'm SOMERA, your coaching companion. How are you feeling today?"
            save_voice_message_async(call_id, "assistant", response_text)
        else:
            history = custom_llm_conversation_histories.get(call_id, [])
            
            try:
                from readiness_scoring import calculate_readiness_score
                from somera_engine import is_closure_signal, is_booking_request, get_voice_friendly_booking_response
                
                readiness_result = calculate_readiness_score(user_message, history)
                readiness_score = readiness_result.get("total_score", 0)
                readiness_rec = readiness_result.get("recommendation", "explore")
                
                save_voice_message_async(call_id, "user", user_message, readiness_score, readiness_rec)
                
                closure = is_closure_signal(user_message, history)
                booking = is_booking_request(user_message)
                
                skip_voice_optimization = False
                should_end_call = False
                
                if booking:
                    response_text = get_voice_friendly_booking_response()
                    skip_voice_optimization = True
                    print(f"[VAPI Custom LLM] Booking request detected - providing voice-friendly booking info")
                elif closure["is_strong"]:
                    response_text = "It was wonderful talking with you today. I'm glad I could be here for you. Take care of yourself, and remember, you can always come back whenever you need support. Goodbye!"
                    should_end_call = True
                    print(f"[VAPI Custom LLM] Strong closure detected: {closure['pattern_matched']} - will end call")
                elif closure["is_closing"]:
                    response_text = "I'm so glad we could have this conversation. Before we wrap up, is there anything else on your mind you'd like to explore? If not, I wish you all the best on your journey."
                    print(f"[VAPI Custom LLM] Soft closure detected: {closure['pattern_matched']}")
                else:
                    response_data = generate_somera_response(
                        user_message=user_message,
                        conversation_history=history
                    )
                    response_text = response_data.get("response", "I'm here to listen. Could you tell me more?")
                
                if not skip_voice_optimization:
                    response_text = optimize_response_for_voice(response_text)
                
                save_voice_message_async(call_id, "assistant", response_text)
                
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": response_text})
                custom_llm_conversation_histories[call_id] = history[-20:]
                
                elapsed_ms = (timing_module.time() - request_start) * 1000
                print(f"[VAPI Custom LLM] SOMERA response: {response_text[:100]}...")
                print(f"[VAPI Custom LLM] Readiness: {readiness_score:.0%} ({readiness_rec})")
                print(f"[VAPI Custom LLM] Response latency: {elapsed_ms:.0f}ms")
                
            except Exception as e:
                print(f"[VAPI Custom LLM] SOMERA error: {e}")
                response_text = "I'm here with you. Could you share that with me again?"
        
        if stream:
            return stream_openai_response(response_text, call_id, end_call=should_end_call)
        else:
            return jsonify({
                "id": f"chatcmpl-{call_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": "somera-voice-1",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_message.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(user_message.split()) + len(response_text.split())
                }
            })
            
    except Exception as e:
        print(f"[VAPI Custom LLM] Error: {e}")
        return jsonify({"error": str(e)}), 500


def stream_openai_response(response_text: str, call_id: str, end_call: bool = False):
    """
    Stream response in OpenAI SSE format for real-time voice.
    
    VAPI expects SSE with 'data: {...}' format matching OpenAI's streaming.
    First chunk MUST include 'role: assistant' for OpenAI-compatible clients.
    
    Args:
        response_text: The text to speak
        call_id: Unique call identifier
        end_call: If True, include endCall tool call to terminate the VAPI call
    """
    import time
    import json
    
    def generate():
        chunk_id = f"chatcmpl-{call_id}"
        
        role_chunk = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "somera-voice-1",
            "choices": [{
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": ""
                },
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(role_chunk)}\n\n"
        
        words = response_text.split()
        chunk_size = 3
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if i > 0:
                chunk_text = " " + chunk_text
            
            chunk_data = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "somera-voice-1",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "content": chunk_text
                    },
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
        
        if end_call:
            tool_call_chunk = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "somera-voice-1",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "tool_calls": [{
                            "id": f"call_endCall_{call_id[:8]}",
                            "type": "function",
                            "function": {
                                "name": "endCall",
                                "arguments": "{}"
                            }
                        }]
                    },
                    "finish_reason": "tool_calls"
                }]
            }
            yield f"data: {json.dumps(tool_call_chunk)}\n\n"
            print(f"[VAPI Custom LLM] Sent endCall tool call to terminate call {call_id}")
        else:
            done_data = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "somera-voice-1",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(done_data)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("WEBHOOK_PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
