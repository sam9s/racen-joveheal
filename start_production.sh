#!/bin/bash
# Production startup script
# Next.js uses PORT env var (set by Autoscale), Flask on 8080

set -e

# Use deployment PORT or default to 5000 for local testing
APP_PORT="${PORT:-5000}"

echo "[Startup] PORT=$APP_PORT"
echo "[Startup] Current directory: $(pwd)"

# CRITICAL: Fail fast if .next folder is missing
if [ ! -d ".next" ]; then
    echo "[ERROR] .next folder missing! Build required before deploy."
    exit 1
fi

echo "[Startup] .next folder found:"
ls -la .next 2>&1 | head -5

echo "[Startup] Starting Next.js on port $APP_PORT..."

# Start Next.js using npx (more reliable than direct node path)
npx next start -p "$APP_PORT" -H 0.0.0.0 &
NEXT_PID=$!

# Wait for Next.js to be ready
sleep 3

# Verify Next.js is running
if kill -0 $NEXT_PID 2>/dev/null; then
    echo "[Startup] Next.js started successfully (PID: $NEXT_PID)"
else
    echo "[ERROR] Next.js failed to start!"
    exit 1
fi

echo "[Startup] Starting Flask on port 8080..."
python webhook_server.py &
FLASK_PID=$!

echo "[Startup] Services started - Next.js on $APP_PORT, Flask on 8080"

# Wait for both processes
wait
