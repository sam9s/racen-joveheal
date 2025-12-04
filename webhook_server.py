"""
Webhook Server for Multi-Channel Messaging

Flask-based API server handling:
- WhatsApp webhooks (via Twilio)
- Instagram webhooks (via Meta Graph API)
- Direct API access for custom integrations
- React frontend API endpoints
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from channel_handlers import (
    whatsapp_handler,
    instagram_handler,
    process_channel_message,
    get_channel_status
)
from chatbot_engine import generate_response
from conversation_logger import log_feedback, log_conversation, ensure_session_exists
from database import get_or_create_user, get_user_conversation_history

app = Flask(__name__)
CORS(app)

conversation_histories = {}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
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
    
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
        
        if is_returning_user and user_id:
            past_history = get_user_conversation_history(user_id, limit=50)
            if past_history:
                for conv in past_history:
                    conversation_histories[session_id].append({"role": "user", "content": conv['question']})
                    conversation_histories[session_id].append({"role": "assistant", "content": conv['answer']})
    
    if conversation_history and not conversation_histories[session_id]:
        conversation_histories[session_id] = conversation_history
    
    result = generate_response(message, conversation_histories[session_id])
    
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
    
    return jsonify({
        "response": result.get("response", "I apologize, but I encountered an issue. Please try again."),
        "sources": result.get("sources", []),
        "safety_triggered": result.get("safety_triggered", False),
        "session_id": session_id,
        "user_id": user_id,
        "is_returning_user": is_returning_user
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


if __name__ == "__main__":
    port = int(os.environ.get("WEBHOOK_PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
