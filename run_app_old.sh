#!/bin/bash
echo "Starting Insight Engine V2 Natively..."

# Install dependencies if needed (native environment as requested)
pip install -r requirements.txt --quiet

# Start the backend in the background
echo "Starting Backend (FastAPI) on http://localhost:8000"
python3 app.py &

# Note: The frontend is a static index.html. You can just open it in a browser
# or serve it with a simple python server if you want it on a port.
echo "Starting Frontend on http://localhost:8080"
python3 -m http.server 8080 --directory . 
