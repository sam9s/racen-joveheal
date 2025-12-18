#!/bin/bash
# Production startup script for Replit Autoscale
# Next.js MUST run in foreground to keep deployment alive

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

# Start Flask webhook server in BACKGROUND first
echo "[Startup] Starting Flask on port 8080 (background)..."
python webhook_server.py &
FLASK_PID=$!
echo "[Startup] Flask started (PID: $FLASK_PID)"

# Give Flask a moment to start
sleep 2

# Start Next.js in FOREGROUND (CRITICAL for Autoscale - keeps deployment alive)
echo "[Startup] Starting Next.js on port $APP_PORT (foreground)..."
exec npx next start -p "$APP_PORT" -H 0.0.0.0
