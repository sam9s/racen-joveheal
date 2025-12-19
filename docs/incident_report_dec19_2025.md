# Incident Report: December 19, 2025 - Production Chat Failure

## Executive Summary

On December 19, 2025, the production widget and chat functionality experienced intermittent failures. Users could load the website (200 response) but could not use the chat feature. This is the second production incident in two consecutive days.

**Root Cause**: Flask backend was inaccessible from external requests while Next.js continued serving pages normally.

**Resolution Time**: ~30 minutes

**Impact**: Widget on client's Kajabi website was non-functional for an unknown period.

---

## Timeline

| Time (Approx) | Event |
|---------------|-------|
| Unknown | Production deployment recycled (Autoscale behavior) |
| Unknown | Flask may have crashed or failed to start properly |
| Unknown | Next.js continued serving pages (200 status) but chat API failed |
| 11:49 UTC | User reported widget/chat not working |
| 11:50 UTC | Investigation started |
| 11:52 UTC | Identified /health returning 500 |
| 11:55 UTC | Created Next.js /health endpoint |
| 11:57 UTC | User republished |
| 12:00 UTC | Confirmed all endpoints working |

---

## Root Cause Analysis

### Immediate Cause
The `/health` endpoint only existed in Flask (port 8080), not in Next.js (port 5000). Since production only exposes port 5000, external health checks to `/health` were failing with 500 error.

### Underlying Cause
The architecture has a fundamental gap: **Next.js and Flask run independently with no dependency checking**.

| Component | Port | External Access | Supervision |
|-----------|------|-----------------|-------------|
| Next.js | 5000 | ✅ Yes | ✅ Autoscale monitors PID 1 |
| Flask | 8080 | ❌ No (internal only) | ❌ No supervision |

When Flask crashes or fails to start:
- Next.js keeps running → Pages return 200
- Chat API fails → Widget shows errors
- No alerts → Issue goes unnoticed until user reports

### Why Internal Dev Works But Production Fails

| Environment | How It Works | Supervision |
|-------------|--------------|-------------|
| **Development (Replit)** | Workflows run separately, each monitored | Replit UI shows workflow status |
| **Production (Autoscale)** | Single startup script, only PID 1 monitored | If Flask dies, nothing notices |

---

## Pattern Analysis: Two Days of Incidents

### December 18, 2025 - Deployment Failure
| Aspect | Details |
|--------|---------|
| **Symptom** | Production returning 404, then deployment torn down |
| **Root Cause** | Next.js was backgrounded (`&`) instead of running in foreground |
| **Why It Surfaced** | Deployment recycling exposed latent bug |
| **Fix** | Changed to `exec npx next start` (foreground) |

### December 19, 2025 - Chat Failure
| Aspect | Details |
|--------|---------|
| **Symptom** | Pages load (200) but chat doesn't work |
| **Root Cause** | Flask not accessible externally, no health route in Next.js |
| **Why It Surfaced** | Likely Flask crash or slow start during deployment |
| **Fix** | Added /health to Next.js, added Flask startup checks |

### Common Pattern
Both incidents share a root cause: **Production has less supervision than development**.

---

## Changes Made Today

### 1. Added Next.js Health Endpoint
**File**: `src/app/health/route.ts`

```typescript
// Checks both Next.js and Flask health
// Returns combined status
```

### 2. Improved Startup Script
**File**: `start_production.sh`

**Before**:
```bash
python webhook_server.py &
sleep 2
exec npx next start
```

**After**:
```bash
python webhook_server.py &

# Wait for Flask to be healthy (up to 30 seconds)
while ! curl -s http://localhost:8080/health; do
    sleep 1
done

# Background monitor - exits if Flask dies
monitor_flask &

exec npx next start
```

---

## Remaining Gaps & Risks

| Risk | Current State | Recommendation |
|------|---------------|----------------|
| **No external monitoring** | None | Set up UptimeRobot immediately |
| **Flask crash during runtime** | New monitor added, untested in production | Verify after next deployment |
| **Knowledge base init timeout** | Could delay Flask startup | Add timeout logging |
| **No alerting** | Manual discovery only | Email/SMS alerts via UptimeRobot |
| **Cold start issues** | Autoscale can recycle anytime | Consider Reserved VM ($20/mo) |

---

## Action Plan

### Immediate (Today)

| Action | Status | Owner |
|--------|--------|-------|
| Add /health to Next.js | ✅ Done | Agent |
| Add Flask startup guard | ✅ Done | Agent |
| Add Flask runtime monitor | ✅ Done | Agent |
| Republish with changes | ✅ Done | Sam |
| Verify production working | ✅ Done | Agent |

### Short-Term (This Week)

| Action | Status | Owner |
|--------|--------|-------|
| Set up UptimeRobot monitoring | ⏳ Pending | Sam |
| Monitor: Homepage | ⏳ Pending | Sam |
| Monitor: /health endpoint | ⏳ Pending | Sam |
| Monitor: /widget.js | ⏳ Pending | Sam |
| Test chat functionality probe | ⏳ Pending | Sam |

### Long-Term (Consider)

| Action | Benefit | Cost |
|--------|---------|------|
| Upgrade to Reserved VM | Eliminates cold starts, faster recovery | $20/month |
| Add Sentry/error tracking | Catch errors before users report | Free tier available |
| Implement graceful degradation | Widget shows "maintenance" instead of error | Development time |
| Move to self-hosted VPS (Dokploy) | Full control, no Autoscale issues | $10-20/month + setup |

---

## UptimeRobot Setup Instructions

1. Go to https://uptimerobot.com (free account)
2. Create these monitors:

| Monitor Name | URL | Type | Interval |
|--------------|-----|------|----------|
| JoveHeal Homepage | https://jove-heal-chatbot--sam9s.replit.app/ | HTTP(s) | 5 min |
| JoveHeal Health | https://jove-heal-chatbot--sam9s.replit.app/health | HTTP(s) | 5 min |
| JoveHeal Widget | https://jove-heal-chatbot--sam9s.replit.app/widget.js | HTTP(s) | 5 min |

3. Add your email for alerts
4. Optional: Add SMS alerts for critical monitors

---

## Lessons Learned

1. **Development ≠ Production**: Just because it works locally doesn't mean production is safe
2. **Pages loading ≠ App working**: HTTP 200 doesn't mean all features work
3. **Monitoring is mandatory**: Without UptimeRobot, we only learn about issues when users complain
4. **Document everything**: These RCAs help prevent repeat issues

---

## Conclusion

This incident was caused by architectural gaps between development and production environments. The fixes implemented today (health endpoint, startup guards, runtime monitoring) should prevent similar issues. However, **external monitoring (UptimeRobot) is critical** and must be set up immediately to catch future issues before the client notices them.

---

*Report Generated: December 19, 2025*
*Author: Replit Agent*
