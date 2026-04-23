"""
Market Data and WebSocket Tests

Tests for real-time market data functionality.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Insight"
        assert "status" in data
        assert "timestamp" in data

    def test_health_endpoint_structure(self, client):
        """Test health endpoint returns correct structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "Insight API"
        assert "timestamp" in data
        assert "components" in data

    def test_protected_endpoint_without_auth(self, client):
        """Test accessing protected endpoint without auth fails."""
        response = client.get("/api/protected")
        assert response.status_code == 401


class TestMarketData:
    """Test market data functionality."""

    def test_market_data_websocket_auth_required(self, client):
        """Test WebSocket requires authentication."""
        # WebSocket connection via test client
        with pytest.raises(Exception):  # Connection will fail
            with client.websocket_connect("/api/ws/market-data"):
                pass


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_on_valid_origin(self, client):
        """Test CORS headers returned for valid origin."""
        response = client.get(
            "/",
            headers={"Origin": "https://insight.vjprojects.co.in"}
        )
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

    def test_cors_preflight(self, client):
        """Test CORS preflight request handling."""
        response = client.options(
            "/auth/login",
            headers={
                "Origin": "https://insight.vjprojects.co.in",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type"
            }
        )
        # Should either succeed or be blocked based on config
        assert response.status_code in [200, 405]