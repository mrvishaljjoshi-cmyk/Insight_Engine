#!/bin/bash
# Insight Engine - Development Setup Script
# Usage: ./scripts/setup_dev.sh

set -e

echo "========================================"
echo "  Insight Engine - Dev Setup"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create virtual environment if not exists
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate venv and install dependencies
echo "Installing dependencies..."
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt 2>/dev/null || echo "No requirements.txt found"

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p backend/logs

# Copy .env if not exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "Please edit .env and add your SECRET_KEY and ENCRYPTION_KEY"
    else
        echo "Warning: No .env or .env.example found"
    fi
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --port 8001"
echo ""
echo "To start the frontend (in another terminal):"
echo "  cd frontend_native"
echo "  python3 -m http.server 8081"
echo ""