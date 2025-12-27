# RACEN Security Action Plan

*Blueprint for Conversational AI Chatbot Security*

**RACEN** = Rapid Automation Client Engagement Network  
*A product line under Raven Solutions Business Process Automation*

---

## Overview

This document serves as a security blueprint for all RACEN conversational AI chatbots. Apply these security measures to protect against DDoS attacks, API cost abuse, and automated scripts.

### Applicable Bots

| Bot Name | Product | Status |
|----------|---------|--------|
| Jovee | JoveHeal | Implemented |
| SOMERA | JoveHeal | Implemented |
| GRESTA | GREST | Apply this blueprint |
| Naira | Nature Mania | Apply this blueprint |

---

## Security Layer 1: Rate Limiting

### Purpose
Prevent automated scripts and attackers from overwhelming the API or draining OpenAI credits.

### Implementation

Create a `rate_limiter.py` module with the following thresholds:

```python
RateLimiter(
    requests_per_minute=10,    # Soft limit - blocks after 10 requests/minute
    requests_per_hour=50,      # Block for 10 minutes after 50/hour
    requests_per_day=100,      # Block for 24 hours after 100/day
    captcha_threshold=20,      # Trigger CAPTCHA after 20 messages in session
    block_duration_minutes=10  # Duration of temporary blocks
)
```

### Key Features

1. **IP-based tracking** - Uses `X-Forwarded-For` header for real client IP behind proxies
2. **Session-based counting** - Tracks messages per session for CAPTCHA trigger
3. **Auto-cleanup** - Removes requests older than 24 hours to prevent memory bloat
4. **Graceful degradation** - Returns user-friendly error messages

### Rate Limiter Code Structure

```python
class RateLimiter:
    def check_rate_limit(ip, session_id) -> (allowed, reason, captcha)
    def record_request(ip, session_id)
    def log_request(ip, session_id, endpoint, message_preview)
    def verify_captcha(session_id, user_answer) -> bool
    def get_stats() -> dict  # For monitoring
    def get_ip_activity(ip) -> dict  # For forensics

def get_client_ip(request) -> str:
    # Extract real IP from X-Forwarded-For or X-Real-IP headers
```

---

## Security Layer 2: IP Logging

### Purpose
Enable forensic analysis and identify abuse patterns.

### What to Log

```python
log_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "ip": client_ip,
    "session_id": session_id,
    "endpoint": "/api/chat/stream",
    "message_preview": message[:50]  # First 50 chars only
}
```

### Storage
- In-memory list (sufficient for single-instance Replit)
- Auto-trim to last 5,000 entries when exceeding 10,000
- For multi-instance: Consider Redis or database storage

---

## Security Layer 3: CAPTCHA Protection

### Purpose
Block automated scripts while allowing legitimate users to continue.

### Widget-Compatible Design

Since chatbots are often embedded in iframes (e.g., Kajabi widgets), use **inline CAPTCHA** that doesn't require page refresh:

```python
def _generate_captcha(session_id) -> dict:
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b
    return {
        "type": "math",
        "question": f"What is {a} + {b}?",
        "answer": str(answer)
    }
```

### Frontend Handling

```javascript
if (response.status === 429) {
    const errorData = await response.json();
    if (errorData.captcha_required) {
        const userAnswer = prompt(errorData.captcha?.question);
        if (userAnswer) {
            // Retry with captcha_answer in request body
            const retryResponse = await fetch(endpoint, {
                body: JSON.stringify({
                    ...originalBody,
                    captcha_answer: userAnswer,
                }),
            });
        }
    }
}
```

---

## Security Layer 4: API Endpoint Protection

### Apply to All Chat Endpoints

For Flask backends, add this check at the start of each chat endpoint:

```python
@app.route("/api/chat/stream", methods=["POST"])
def api_chat_stream():
    data = request.get_json()
    session_id = data.get("session_id", "anonymous")
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Check for CAPTCHA answer
    captcha_answer = data.get("captcha_answer")
    if captcha_answer:
        if not rate_limiter.verify_captcha(session_id, captcha_answer):
            return jsonify({"error": "Incorrect answer", "captcha_failed": True}), 400
    
    # Check rate limit
    allowed, reason, captcha = rate_limiter.check_rate_limit(client_ip, session_id)
    if not allowed:
        if captcha:
            return jsonify({
                "error": reason,
                "captcha_required": True,
                "captcha": captcha
            }), 429
        return jsonify({"error": reason, "rate_limited": True}), 429
    
    # Log and record the request
    rate_limiter.log_request(client_ip, session_id, "/api/chat/stream", message[:50])
    rate_limiter.record_request(client_ip, session_id)
    
    # Continue with normal chat processing...
```

---

## Security Layer 5: Monitoring Endpoint

### Admin Stats Endpoint

```python
@app.route("/api/admin/rate-limiter/stats", methods=["GET"])
def rate_limiter_stats():
    # Protect with internal API key
    if not validate_internal_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify(rate_limiter.get_stats())
```

### Stats Response

```json
{
    "active_ips": 42,
    "blocked_ips": 3,
    "pending_captchas": 1,
    "total_logged_requests": 1523,
    "blocked_ip_list": ["192.168.1.1", "10.0.0.5"]
}
```

---

## Security Layer 6: Content Safety Guardrails

### Already Implemented in RACEN Bots

1. **Crisis Detection** - Detect keywords like "suicide", "self-harm" and redirect to professional resources
2. **Medical/Mental Health Filtering** - Decline to give medical advice
3. **PII Protection** - Never ask for or store email, phone, address
4. **Non-judgmental Language** - LLM critic ensures empathetic responses

---

## Implementation Checklist

Apply to each new RACEN chatbot:

- [ ] Create `rate_limiter.py` with RateLimiter class
- [ ] Add import: `from rate_limiter import rate_limiter, get_client_ip`
- [ ] Add rate limit checks to ALL chat endpoints
- [ ] Add CAPTCHA handling to frontend error handling
- [ ] Add `/api/admin/rate-limiter/stats` monitoring endpoint
- [ ] Test with rapid requests (should block on 11th request)
- [ ] Verify CAPTCHA triggers after 20 messages
- [ ] Apply content safety guardrails (crisis, medical, PII)

---

## Testing Rate Limiting

### Quick Test Script

```python
import requests

url = 'http://localhost:8080/api/chat/stream'
session_id = 'test_session'

for i in range(12):
    response = requests.post(url, 
        json={'message': 'Hello', 'session_id': session_id}
    )
    if response.status_code == 429:
        print(f'Request {i+1}: RATE LIMITED - {response.json()["error"]}')
        break
    else:
        print(f'Request {i+1}: OK')
```

**Expected Result:** Requests 1-10 succeed, Request 11 blocked with "Too many requests. Please wait a minute."

---

## Cost Protection Summary

| Threat | Protection | Recovery |
|--------|------------|----------|
| Script flooding (10+ req/min) | Rate limit | Auto-unblock after 1 min |
| Sustained abuse (50+ req/hr) | 10-min block | Auto-unblock |
| Heavy abuse (100+ req/day) | 24-hour block | Auto-unblock |
| Bot automation | CAPTCHA after 20 msgs | Pass challenge to continue |
| Attack analysis | IP logging | Review logs for patterns |

---

## Notes

- **In-memory storage**: Current implementation uses in-memory dicts. For production multi-instance deployments, consider Redis.
- **HTTPS**: All Replit deployments use HTTPS by default - data in transit is encrypted.
- **Database encryption at rest**: Not implemented (overkill for coaching chat, consider for financial data).

---

*Document Version: 1.0*  
*Created: December 27, 2025*  
*Applicable to: All RACEN conversational AI chatbots*
