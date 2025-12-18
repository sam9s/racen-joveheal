#!/bin/bash
# Production startup script
# Next.js on port 5000 (Autoscale requirement), Flask on port 8080

set -e

echo "[Startup] Current directory: $(pwd)"
echo "[Startup] Checking for .next folder..."
ls -la .next 2>&1 | head -5 || echo "[ERROR] .next folder missing!"

echo "[Startup] Starting Next.js on port 5000..."

# Start Next.js FIRST on port 5000 - required for Autoscale
node node_modules/next/dist/bin/next start -p 5000 -H 0.0.0.0 &
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

echo "[Startup] Services started - Next.js (PID: $NEXT_PID), Flask (PID: $FLASK_PID)"

# Wait for both processes
wait
