#!/bin/bash
# Production startup script for Replit Autoscale
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

echo "[Startup] Starting Flask on port 8080 (background)..."
python webhook_server.py &
FLASK_PID=$!
echo "[Startup] Flask started (PID: $FLASK_PID)"

echo "[Startup] Waiting for Flask to be healthy..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "[Startup] Flask is healthy!"
        break
    fi
    
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "[ERROR] Flask process died during startup!"
        exit 1
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "[Startup] Waiting for Flask... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[ERROR] Flask did not become healthy in time!"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

monitor_flask() {
    while true; do
        sleep 30
        if ! kill -0 $FLASK_PID 2>/dev/null; then
            echo "[CRITICAL] Flask process died! Exiting to trigger restart..."
            exit 1
        fi
        if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo "[CRITICAL] Flask health check failed! Exiting to trigger restart..."
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
