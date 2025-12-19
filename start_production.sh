#!/bin/bash
# Production startup script for Replit Autoscale/Reserved VM
# This script ensures both Flask and Next.js run together
# If either fails, the entire deployment restarts

set -e

APP_PORT="${PORT:-5000}"

echo "[Startup] PORT=$APP_PORT"
echo "[Startup] Current directory: $(pwd)"

if [ ! -d ".next" ]; then
    echo "[ERROR] .next folder missing! Build required before deploy."
    exit 1
fi

echo "[Startup] .next folder found"

cleanup() {
    echo "[Shutdown] Cleaning up processes..."
    kill $FLASK_PID 2>/dev/null || true
    kill $NEXTJS_PID 2>/dev/null || true
    exit 1
}

trap cleanup SIGTERM SIGINT

echo "[Startup] Starting Flask with Gunicorn on port 8080..."
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
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "[ERROR] Gunicorn process died during startup!"
        exit 1
    fi
    
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

echo "[Startup] Starting Next.js on port $APP_PORT..."
npx next start -p "$APP_PORT" -H 0.0.0.0 &
NEXTJS_PID=$!
echo "[Startup] Next.js started (PID: $NEXTJS_PID)"

sleep 3
if ! kill -0 $NEXTJS_PID 2>/dev/null; then
    echo "[ERROR] Next.js failed to start!"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

echo "[Startup] All services running. Monitoring..."
echo "[Startup] Flask PID: $FLASK_PID, Next.js PID: $NEXTJS_PID"

while true; do
    sleep 10
    
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "[CRITICAL] Gunicorn process died! Triggering restart..."
        kill $NEXTJS_PID 2>/dev/null || true
        exit 1
    fi
    
    if ! kill -0 $NEXTJS_PID 2>/dev/null; then
        echo "[CRITICAL] Next.js process died! Triggering restart..."
        kill $FLASK_PID 2>/dev/null || true
        exit 1
    fi
    
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")
    if [ "$HEALTH_RESPONSE" != "200" ]; then
        echo "[CRITICAL] Flask health check failed (HTTP: $HEALTH_RESPONSE)! Triggering restart..."
        kill $FLASK_PID 2>/dev/null || true
        kill $NEXTJS_PID 2>/dev/null || true
        exit 1
    fi
done
