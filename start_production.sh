#!/bin/bash
# Production startup script
# Next.js on port 5000 (Autoscale requirement), Flask on port 8080

echo "[Startup] Starting Next.js on port 5000..."

# Start Next.js FIRST on port 5000 - this is required for Autoscale
npx next start -p 5000 -H 0.0.0.0 &
NEXT_PID=$!

# Give Next.js a moment to bind port 5000
sleep 2

echo "[Startup] Starting Flask on port 8080..."
python webhook_server.py &
FLASK_PID=$!

echo "[Startup] Services started - Next.js (PID: $NEXT_PID), Flask (PID: $FLASK_PID)"

# Wait for both processes
wait
