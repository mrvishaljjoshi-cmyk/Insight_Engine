#!/bin/bash
# Insight Engine - Database Migration Script
# Usage: ./scripts/migrate_db.sh [up|down|status]

set -e

ACTION="${1:-up}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR/backend"

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "========================================"
echo "  Database Migration - $ACTION"
echo "========================================"
echo ""

case $ACTION in
    up)
        echo "Running migrations..."
        alembic upgrade head
        ;;
    down)
        echo "Rolling back last migration..."
        alembic downgrade -1
        ;;
    status)
        echo "Migration status:"
        alembic current
        echo ""
        echo "History:"
        alembic history
        ;;
    create)
        if [ -n "$2" ]; then
            echo "Creating migration: $2"
            alembic revision --message="$2"
        else
            echo "Usage: $0 create \"migration message\""
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {up|down|status|create \"message\"}"
        exit 1
        ;;
esac

echo ""
echo "Done!"