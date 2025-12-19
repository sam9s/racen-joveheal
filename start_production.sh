#!/bin/bash
# Production startup script for Replit Autoscale/Reserved VM
# Next.js MUST run in foreground to keep deployment alive
# Flask MUST be healthy before Next.js starts

set -e

APP_PORT="${PORT:-5000}"

echo "[Startup] PORT=$APP_PORT"
echo "[Startup] Current directory: $(pwd)"

if [ ! -d ".next" ]; then
    echo "[ERROR] .next folder missing! Build required before deploy."
    exit 1
fi

echo "[Startup] .next folder found"

echo "[Startup] Starting Flask with Gunicorn on port 8080 (background)..."
# Using gunicorn with gevent worker for production:
# - Single worker (-w 1) sufficient for our workload
# - Gevent handles concurrent connections efficiently
# - Timeout of 120s for long-running requests (streaming)
gunicorn webhook_server:app \
    --bind 0.0.0.0:8080 \
    --worker-class gevent \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --capture-output &
FLASK_PID=$!
echo "[Startup] Gunicorn started (PID: $FLASK_PID)"

echo "[Startup] Waiting for Flask to be healthy..."
MAX_RETRIES=60
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Check if gunicorn process is still alive
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "[ERROR] Gunicorn process died during startup!"
        exit 1
    fi
    
    # Check health endpoint
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")
    if [ "$HEALTH_RESPONSE" = "200" ]; then
        echo "[Startup] Flask is healthy!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "[Startup] Waiting for Flask... ($RETRY_COUNT/$MAX_RETRIES) [HTTP: $HEALTH_RESPONSE]"
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[ERROR] Flask did not become healthy in time!"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

# Monitor function - runs in background, exits deployment if Flask dies
monitor_flask() {
    while true; do
        sleep 30
        
        # Check if gunicorn process is alive
        if ! kill -0 $FLASK_PID 2>/dev/null; then
            echo "[CRITICAL] Gunicorn process died! Exiting to trigger restart..."
            exit 1
        fi
        
        # Check health endpoint returns 200
        HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")
        if [ "$HEALTH_RESPONSE" != "200" ]; then
            echo "[CRITICAL] Flask health check failed (HTTP: $HEALTH_RESPONSE)! Exiting to trigger restart..."
            kill $FLASK_PID 2>/dev/null || true
            exit 1
        fi
    done
}

monitor_flask &
MONITOR_PID=$!
echo "[Startup] Flask monitor started (PID: $MONITOR_PID)"

echo "[Startup] Starting Next.js on port $APP_PORT (foreground)..."
exec npx next start -p "$APP_PORT" -H 0.0.0.0
