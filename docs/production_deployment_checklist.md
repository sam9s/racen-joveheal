# Production Deployment Checklist for Replit

**Purpose:** This document captures all production deployment protections and learnings from JoveHeal. Apply these before taking any project live on Replit.

---

## 1. Choose Reserved VM (Not Autoscale)

**Cost:** $20/month (vs Autoscale ~$50/week for always-on)

**Why Reserved VM:**
- Always running (no cold starts)
- No auto-shutdown after idle period
- Predictable billing
- Better for services that need 24/7 availability

**Autoscale Problems We Encountered:**
- Scaled to zero after inactivity, causing 404 errors
- Cold starts took 30-60 seconds
- PID 1 monitoring caused unexpected shutdowns
- Cost adds up quickly for always-on requirements

---

## 2. Production Server Configuration

### For Python/Flask Backend

**NEVER use Flask's development server in production:**
```python
# WRONG - Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

**USE Gunicorn (production WSGI server):**
```bash
# Install
pip install gunicorn gevent

# Run command
gunicorn --bind 0.0.0.0:8080 --workers 2 --worker-class gevent --timeout 120 webhook_server:app
```

**Why Gunicorn:**
- Handles concurrent requests properly
- Process management and auto-restart of workers
- Production-grade stability
- Better memory management

### For Node.js/Next.js Frontend

**Always build before production:**
```bash
npx next build
```

**Run production server (not dev):**
```bash
npx next start -p 5000 -H 0.0.0.0
```

---

## 3. Process Supervision (Critical for Replit)

### The PID 1 Rule

Replit monitors PID 1 (the main process). If PID 1 exits, the deployment is torn down.

**Pattern: Shell script as PID 1 supervising both services:**

```bash
#!/bin/bash
set -e

FLASK_PORT="${FLASK_PORT:-8080}"
APP_PORT="${PORT:-5000}"

echo "Starting Flask backend on port $FLASK_PORT..."
gunicorn --bind 0.0.0.0:$FLASK_PORT --workers 2 --worker-class gevent \
    --timeout 120 webhook_server:app &
FLASK_PID=$!

# Wait for Flask to be healthy
MAX_RETRIES=30
RETRY_COUNT=0
echo "Waiting for Flask to be healthy..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "http://localhost:$FLASK_PORT/health" > /dev/null 2>&1; then
        echo "Flask is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Flask failed to start"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

echo "Starting Next.js frontend on port $APP_PORT..."
npx next start -p "$APP_PORT" -H 0.0.0.0 &
NEXTJS_PID=$!

# Trap signals and forward to children
trap "kill $FLASK_PID $NEXTJS_PID 2>/dev/null; exit" SIGTERM SIGINT

# Monitor both processes - if either dies, exit (triggering restart)
while true; do
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask died, exiting..."
        kill $NEXTJS_PID 2>/dev/null || true
        exit 1
    fi
    if ! kill -0 $NEXTJS_PID 2>/dev/null; then
        echo "Next.js died, exiting..."
        kill $FLASK_PID 2>/dev/null || true
        exit 1
    fi
    sleep 5
done
```

**Key Points:**
- Shell script stays alive as PID 1
- Both services run in background
- Monitor loop checks both processes every 5 seconds
- If either dies, script exits → Replit restarts everything
- Signal trapping ensures clean shutdown

---

## 4. Health Endpoints (Required)

### Flask Health Endpoint

```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Flask Backend",
        "timestamp": datetime.now().isoformat()
    })
```

### Next.js Health Endpoint

Create `src/app/health/route.ts`:

```typescript
import { NextResponse } from 'next/server';

export async function GET() {
  const FLASK_URL = process.env.FLASK_URL || 'http://localhost:8080';
  
  try {
    const flaskResponse = await fetch(`${FLASK_URL}/health`, {
      method: 'GET',
      cache: 'no-store',
      signal: AbortSignal.timeout(5000)
    });
    
    const flaskHealthy = flaskResponse.ok;
    
    return NextResponse.json({
      status: flaskHealthy ? 'healthy' : 'degraded',
      service: 'Your Application',
      components: {
        nextjs: 'healthy',
        flask: flaskHealthy ? 'healthy' : 'unhealthy'
      }
    });
  } catch (error) {
    return NextResponse.json({
      status: 'degraded',
      service: 'Your Application',
      components: {
        nextjs: 'healthy',
        flask: 'unreachable'
      }
    }, { status: 503 });
  }
}
```

**Why Both Endpoints:**
- External monitoring hits Next.js `/health`
- Next.js internally checks Flask health
- Single endpoint gives full system status

---

## 5. Fail-Fast Knowledge Base Validation

If your app uses ChromaDB or any vector database, validate it at startup:

```python
def validate_knowledge_base():
    """Fail fast if knowledge base is broken."""
    try:
        collection = chroma_client.get_collection("your_collection")
        count = collection.count()
        if count == 0:
            raise ValueError("Knowledge base is empty!")
        print(f"Knowledge base validated: {count} documents")
        return True
    except Exception as e:
        print(f"CRITICAL: Knowledge base validation failed: {e}")
        sys.exit(1)  # Fail fast - don't start with broken KB
```

**Call this at startup before accepting requests.**

---

## 6. External Monitoring (UptimeRobot)

### Setup (Free Tier)

1. Go to https://uptimerobot.com and create account
2. Add monitors for:
   - **Homepage:** `https://your-app.replit.app/`
   - **Health Endpoint:** `https://your-app.replit.app/health`
   - **Widget (if applicable):** `https://your-app.replit.app/widget.js`

3. Set check interval: 5 minutes
4. Configure alerts:
   - Email notifications
   - **Pushover** for push notifications to phone (recommended)

### Why UptimeRobot:
- Free tier is sufficient
- 5-minute checks catch issues before clients notice
- Push notifications ensure you're alerted immediately
- Status pages for client visibility (optional)

---

## 7. Pre-Deployment Checklist

### Before Publishing

- [ ] `start_production.sh` uses shell as PID 1 with process monitoring
- [ ] Flask uses Gunicorn (not development server)
- [ ] `npx next build` completed successfully
- [ ] `.next` folder exists and is current
- [ ] Health endpoints exist on both services
- [ ] Knowledge base validation runs at startup (if applicable)
- [ ] Environment variables are set in Replit Secrets
- [ ] Reserved VM is selected (not Autoscale)

### After Publishing

- [ ] `/health` returns 200 with all components healthy
- [ ] Main functionality works (test the chat/main feature)
- [ ] UptimeRobot monitors are configured and showing green
- [ ] Test from external network (not just Replit)

---

## 8. Incident Response

### If Production Goes Down

1. **Check deployment logs** in Replit Publishing tab
2. **Check UptimeRobot** for when it went down
3. **Verify in dev environment** - does it work locally?
4. **Check `start_production.sh`** - any recent changes?
5. **Use Replit Checkpoints** to rollback if needed

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| 404 on all routes | Autoscale scaled to zero | Switch to Reserved VM |
| Intermittent 502 | Flask using dev server | Switch to Gunicorn |
| Chat not responding | Flask not accessible | Check health endpoint |
| Slow first response | Cold start | Reserved VM eliminates this |

---

## 9. Cost Summary

| Deployment Type | Cost | Best For |
|----------------|------|----------|
| Reserved VM | $20/month | Production apps, always-on |
| Autoscale | ~$0.000024/sec | Dev/staging, variable traffic |

**Recommendation:** Always use Reserved VM for production apps that need reliability.

---

## 10. Files to Create/Modify

1. **`start_production.sh`** - Main startup script (see Section 3)
2. **`src/app/health/route.ts`** - Next.js health endpoint
3. **Flask app** - Add `/health` endpoint
4. **Requirements** - Add `gunicorn` and `gevent`

---

## Quick Reference Commands

```bash
# Build Next.js
npx next build

# Test Flask with Gunicorn locally
gunicorn --bind 0.0.0.0:8080 --workers 2 webhook_server:app

# Check production health
curl https://your-app.replit.app/health

# View production logs (in Replit)
# Publishing tab → View Logs
```

---

**Document Version:** 1.0  
**Last Updated:** December 19, 2025  
**Based on:** JoveHeal production incidents and fixes
