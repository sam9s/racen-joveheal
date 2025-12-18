#!/bin/bash
# Production startup script - optimized for fast cold starts
# Static files (widget.js) are served by Next.js immediately
# Flask backend starts in parallel

echo "[Startup] Starting services in parallel for fast cold start..."

# Start Flask backend in background
python webhook_server.py &
FLASK_PID=$!

# Start Next.js immediately - don't wait for Flask
# Static files like widget.js will be available right away
npx next start -p 5000 -H 0.0.0.0 &
NEXT_PID=$!

echo "[Startup] Both services starting (Flask PID: $FLASK_PID, Next.js PID: $NEXT_PID)"

# Quick health check for Flask (non-blocking, just for logging)
sleep 3
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "[Startup] Flask backend ready!"
else
    echo "[Startup] Flask still starting (will be ready shortly)..."
fi

# Wait for both processes
wait
