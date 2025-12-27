"""
Rate Limiter for Chatbot Security

Protects against:
- DDoS attacks
- API cost abuse
- Automated scripts

Features:
- IP-based rate limiting (10/min, 100/day)
- Session-based message counting
- IP logging for forensics
- Simple CAPTCHA challenge after threshold
"""

import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Tuple, Optional
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rate_limiter")

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_hour: int = 50,
        requests_per_day: int = 100,
        captcha_threshold: int = 20,
        block_duration_minutes: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.captcha_threshold = captcha_threshold
        self.block_duration = timedelta(minutes=block_duration_minutes)
        
        self.ip_requests = defaultdict(list)
        self.session_message_counts = defaultdict(int)
        self.blocked_ips = {}
        self.pending_captchas = {}
        self.ip_log = []
        
    def _clean_old_requests(self, ip: str):
        """Remove requests older than 24 hours."""
        now = time.time()
        day_ago = now - 86400
        self.ip_requests[ip] = [t for t in self.ip_requests[ip] if t > day_ago]
    
    def _count_requests_in_window(self, ip: str, seconds: int) -> int:
        """Count requests from IP in the given time window."""
        now = time.time()
        cutoff = now - seconds
        return sum(1 for t in self.ip_requests[ip] if t > cutoff)
    
    def log_request(self, ip: str, session_id: str, endpoint: str, message_preview: str = ""):
        """Log a request for monitoring and forensics."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": ip,
            "session_id": session_id,
            "endpoint": endpoint,
            "message_preview": message_preview[:50] if message_preview else ""
        }
        self.ip_log.append(log_entry)
        
        if len(self.ip_log) > 10000:
            self.ip_log = self.ip_log[-5000:]
        
        logger.info(f"[Request] IP={ip}, Session={session_id[:16]}..., Endpoint={endpoint}")
    
    def check_rate_limit(self, ip: str, session_id: str = None) -> Tuple[bool, str, Optional[dict]]:
        """
        Check if the request should be allowed.
        
        Returns:
            Tuple of (allowed, reason, captcha_challenge)
            - allowed: True if request is allowed
            - reason: Human-readable reason if blocked
            - captcha_challenge: If not None, user must solve this first
        """
        now = time.time()
        
        if ip in self.blocked_ips:
            block_until = self.blocked_ips[ip]
            if datetime.utcnow() < block_until:
                remaining = (block_until - datetime.utcnow()).seconds // 60
                logger.warning(f"[Blocked] IP={ip} blocked for {remaining} more minutes")
                return False, f"Too many requests. Please try again in {remaining} minutes.", None
            else:
                del self.blocked_ips[ip]
        
        self._clean_old_requests(ip)
        
        minute_count = self._count_requests_in_window(ip, 60)
        if minute_count >= self.requests_per_minute:
            logger.warning(f"[Rate Limit] IP={ip} exceeded {self.requests_per_minute}/min limit")
            return False, "Too many requests. Please wait a minute before trying again.", None
        
        hour_count = self._count_requests_in_window(ip, 3600)
        if hour_count >= self.requests_per_hour:
            self.blocked_ips[ip] = datetime.utcnow() + self.block_duration
            logger.warning(f"[Rate Limit] IP={ip} exceeded {self.requests_per_hour}/hour limit, blocked for {self.block_duration}")
            return False, f"Rate limit exceeded. Please try again in {self.block_duration.seconds // 60} minutes.", None
        
        day_count = self._count_requests_in_window(ip, 86400)
        if day_count >= self.requests_per_day:
            self.blocked_ips[ip] = datetime.utcnow() + timedelta(hours=24)
            logger.warning(f"[Rate Limit] IP={ip} exceeded {self.requests_per_day}/day limit, blocked for 24 hours")
            return False, "Daily limit reached. Please try again tomorrow.", None
        
        if session_id:
            session_count = self.session_message_counts.get(session_id, 0)
            if session_count >= self.captcha_threshold:
                if session_id in self.pending_captchas:
                    return False, "Please solve the verification challenge to continue.", self.pending_captchas[session_id]
                else:
                    captcha = self._generate_captcha(session_id)
                    logger.info(f"[CAPTCHA] Triggered for session={session_id[:16]}... (count={session_count})")
                    return False, "Please verify you're human to continue.", captcha
        
        return True, "", None
    
    def record_request(self, ip: str, session_id: str = None):
        """Record a successful request."""
        self.ip_requests[ip].append(time.time())
        if session_id:
            self.session_message_counts[session_id] += 1
    
    def _generate_captcha(self, session_id: str) -> dict:
        """Generate a simple math CAPTCHA."""
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        answer = a + b
        
        captcha = {
            "type": "math",
            "question": f"What is {a} + {b}?",
            "answer": str(answer),
            "session_id": session_id
        }
        self.pending_captchas[session_id] = captcha
        return {"type": "math", "question": captcha["question"]}
    
    def verify_captcha(self, session_id: str, user_answer: str) -> bool:
        """Verify a CAPTCHA answer."""
        if session_id not in self.pending_captchas:
            return True
        
        expected = self.pending_captchas[session_id]["answer"]
        if user_answer.strip() == expected:
            del self.pending_captchas[session_id]
            self.session_message_counts[session_id] = 0
            logger.info(f"[CAPTCHA] Verified for session={session_id[:16]}...")
            return True
        
        logger.warning(f"[CAPTCHA] Failed for session={session_id[:16]}...")
        return False
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics for monitoring."""
        return {
            "active_ips": len(self.ip_requests),
            "blocked_ips": len(self.blocked_ips),
            "pending_captchas": len(self.pending_captchas),
            "total_logged_requests": len(self.ip_log),
            "blocked_ip_list": list(self.blocked_ips.keys())[:10]
        }
    
    def get_ip_activity(self, ip: str) -> dict:
        """Get activity for a specific IP."""
        self._clean_old_requests(ip)
        return {
            "ip": ip,
            "requests_last_minute": self._count_requests_in_window(ip, 60),
            "requests_last_hour": self._count_requests_in_window(ip, 3600),
            "requests_last_day": self._count_requests_in_window(ip, 86400),
            "is_blocked": ip in self.blocked_ips
        }
    
    def reset_session(self, session_id: str):
        """Reset session message count (e.g., when user starts new conversation)."""
        if session_id in self.session_message_counts:
            del self.session_message_counts[session_id]
        if session_id in self.pending_captchas:
            del self.pending_captchas[session_id]


rate_limiter = RateLimiter(
    requests_per_minute=10,
    requests_per_hour=50,
    requests_per_day=100,
    captcha_threshold=20,
    block_duration_minutes=10
)


def get_client_ip(request) -> str:
    """Extract client IP from Flask request, handling proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or "unknown"
