#!/bin/bash
# Pure Native Runner (Zero Venv Manual Activation)
# This script runs the Insight Engine seamlessly.

echo "🚀 Starting Insight Engine Native..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Ensure venv exists, if not, create it silently
if [ ! -d "backend/venv" ]; then
    echo "⚙️  Initializing environment (first run only)..."
    python3 -m venv backend/venv
    backend/venv/bin/pip install --upgrade pip --quiet
    backend/venv/bin/pip install -r backend/requirements.txt --quiet
fi

# Run the backend using the embedded binary directly (no source activate needed)
echo "🌐 Starting Backend API..."
backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --app-dir backend &
BACKEND_PID=$!

echo "⚡ Starting Frontend Web Server..."
python3 -m http.server 8081 --directory frontend_native &
FRONTEND_PID=$!

echo "======================================"
echo "Insight Engine is LIVE!"
echo "Backend API: http://localhost:8001"
echo "Frontend UI: http://localhost:8081"
echo "Press Ctrl+C to stop both servers."
echo "======================================"

trap "kill $BACKEND_PID $FRONTEND_PID; echo '\n🛑 Servers stopped.'; exit 0" SIGINT SIGTERM

wait
