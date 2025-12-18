#!/bin/bash
# Production startup script - optimized for fast cold starts
# Static files (widget.js) are served by Next.js immediately
# Flask backend starts in parallel

echo "[Startup] Starting services in parallel for fast cold start..."

# Use PORT env var for deployment, fallback to 5000 for local dev
APP_PORT="${PORT:-5000}"
export PORT="$APP_PORT"

# Start Flask backend in background
python webhook_server.py &
FLASK_PID=$!

# For standalone mode, we need to ensure static files are in place
if [ -d ".next/standalone" ]; then
    echo "[Startup] Using standalone mode..."
    # Copy public folder and static files to standalone directory
    cp -r public .next/standalone/ 2>/dev/null || true
    cp -r .next/static .next/standalone/.next/ 2>/dev/null || true
    
    # Run standalone server
    cd .next/standalone
    node server.js &
    NEXT_PID=$!
    cd ../..
else
    echo "[Startup] Using regular Next.js start..."
    npx next start -p "$APP_PORT" -H 0.0.0.0 &
    NEXT_PID=$!
fi

echo "[Startup] Both services starting (Flask PID: $FLASK_PID, Next.js PID: $NEXT_PID) on port $APP_PORT"

# Quick health check for Flask (non-blocking, just for logging)
sleep 3
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "[Startup] Flask backend ready!"
else
    echo "[Startup] Flask still starting (will be ready shortly)..."
fi

# Wait for both processes
wait
