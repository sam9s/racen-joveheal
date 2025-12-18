#!/bin/bash
# Production startup script - optimized for fast cold starts
# Next.js serves on port 5000 (required for Autoscale)
# Flask backend runs on port 8080 (internal only)

echo "[Startup] Starting services..."

# Force port 5000 for Next.js (Autoscale requirement)
export PORT=5000
export HOSTNAME="0.0.0.0"

# Start Flask backend in background on port 8080
python webhook_server.py &
FLASK_PID=$!

# For standalone mode, we need to ensure static files are in place
if [ -d ".next/standalone" ]; then
    echo "[Startup] Using standalone mode on port 5000..."
    # Copy public folder and static files to standalone directory
    cp -r public .next/standalone/ 2>/dev/null || true
    cp -r .next/static .next/standalone/.next/ 2>/dev/null || true
    
    # Run standalone server - it reads PORT and HOSTNAME env vars
    cd .next/standalone
    node server.js &
    NEXT_PID=$!
    cd ../..
else
    echo "[Startup] Using regular Next.js start on port 5000..."
    npx next start -p 5000 -H 0.0.0.0 &
    NEXT_PID=$!
fi

echo "[Startup] Next.js (PID: $NEXT_PID) on port 5000, Flask (PID: $FLASK_PID) on port 8080"

# Quick health check for Flask (non-blocking, just for logging)
sleep 3
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "[Startup] Flask backend ready!"
else
    echo "[Startup] Flask still starting (will be ready shortly)..."
fi

# Wait for both processes
wait
