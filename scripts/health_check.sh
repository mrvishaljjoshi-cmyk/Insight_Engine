#!/bin/bash
# Insight Engine - Health Check Script
# Usage: ./scripts/health_check.sh

set -e

echo "========================================"
echo "  Insight Engine Health Check"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API Base URL
API_URL="${1:-http://localhost:8001}"

check_service() {
    local name=$1
    local url=$2

    echo -n "Checking $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

check_db() {
    echo -n "Checking Database... "
    result=$(curl -s "$API_URL/health" 2>/dev/null | grep -o '"database":"connected"' || echo "")
    if [ -n "$result" ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
}

check_redis() {
    echo -n "Checking Redis... "
    result=$(curl -s "$API_URL/health" 2>/dev/null | grep -o '"redis":"connected"' || echo "")
    if [ -n "$result" ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${YELLOW}⚠ NOT CONNECTED (may be optional)${NC}"
    fi
}

check_websocket() {
    echo -n "Checking WebSocket... "
    # Simple check - try to connect
    result=$(curl -s -I "$API_URL/api/ws/market-data" 2>/dev/null | head -1 || echo "failed")
    if echo "$result" | grep -q "401\|400\|101"; then
        echo -e "${GREEN}✓ OK (Auth required)${NC}"
    else
        echo -e "${YELLOW}⚠ CHECK NEEDED${NC}"
    fi
}

# Run checks
echo "Target: $API_URL"
echo ""
check_service "API Root" "$API_URL/"
check_service "API Health" "$API_URL/health"
check_db
check_redis
check_websocket

echo ""
echo "========================================"
echo "  Done"
echo "========================================"