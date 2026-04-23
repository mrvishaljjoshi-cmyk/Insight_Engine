"""
Broker API Tests

Tests for /brokers endpoints: CRUD operations, holdings, positions.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestBrokerEndpoints:
    """Test broker management endpoints."""

    def test_add_broker(self, client, auth_headers):
        """Test adding a new broker connection."""
        response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Zerodha",
                "credentials": {
                    "api_key": "test_key",
                    "access_token": "test_token"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["broker_name"] == "Zerodha"
        # Credentials should be masked
        assert data["credentials"]["api_key"] != "test_key"

    def test_get_brokers_empty(self, client, auth_headers):
        """Test getting brokers when none connected."""
        response = client.get("/brokers/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_brokers_with_data(self, client, auth_headers):
        """Test getting list of connected brokers."""
        # Add a broker first
        client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Angel One",
                "credentials": {
                    "smartapi_key": "ao_key",
                    "client_id": "CLIENT123"
                }
            }
        )

        response = client.get("/brokers/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["broker_name"] == "Angel One"

    def test_get_single_broker(self, client, auth_headers):
        """Test getting a specific broker by ID."""
        # Add broker
        add_response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Zerodha",
                "credentials": {"api_key": "key"}
            }
        )
        broker_id = add_response.json()["id"]

        response = client.get(f"/brokers/{broker_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["broker_name"] == "Zerodha"

    def test_delete_broker(self, client, auth_headers):
        """Test deleting a broker connection."""
        # Add broker
        add_response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Groww",
                "credentials": {"api_key": "key"}
            }
        )
        broker_id = add_response.json()["id"]

        # Delete it
        response = client.delete(f"/brokers/{broker_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Broker disconnected successfully"

        # Verify deleted
        get_response = client.get(f"/brokers/{broker_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_toggle_broker_status(self, client, auth_headers):
        """Test enabling/disabling a broker."""
        # Add broker
        add_response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Dhan",
                "credentials": {"client_id": "dh123"}
            }
        )
        broker_id = add_response.json()["id"]

        # Toggle off
        response = client.patch(f"/brokers/{broker_id}/toggle", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        # Toggle on
        response = client.patch(f"/brokers/{broker_id}/toggle", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is True

    def test_broker_not_found(self, client, auth_headers):
        """Test accessing non-existent broker returns 404."""
        response = client.get("/brokers/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthorized_access(self, client):
        """Test accessing brokers without auth fails."""
        response = client.get("/brokers/")
        assert response.status_code == 401

    def test_add_multiple_brokers(self, client, auth_headers):
        """Test adding multiple brokers."""
        brokers = ["Zerodha", "Angel One", "Groww", "Dhan", "Upstox"]

        for broker_name in brokers:
            response = client.post(
                "/brokers/",
                headers=auth_headers,
                json={
                    "broker_name": broker_name,
                    "credentials": {"test": "value"}
                }
            )
            assert response.status_code == 200

        # Verify all added
        response = client.get("/brokers/", headers=auth_headers)
        assert len(response.json()) == 5


class TestBrokerHoldings:
    """Test broker holdings endpoints."""

    @patch('app.services.broker_factory.BrokerFactory.get_broker')
    def test_get_holdings_success(self, mock_get_broker, client, auth_headers):
        """Test fetching holdings from a broker."""
        # Add broker first
        add_response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Zerodha",
                "credentials": {"api_key": "key", "access_token": "token"}
            }
        )
        broker_id = add_response.json()["id"]

        # Mock broker response
        mock_broker = MagicMock()
        mock_broker.get_holdings.return_value = [
            {"symbol": "RELIANCE", "quantity": 10, "average_price": 2500}
        ]
        mock_get_broker.return_value = mock_broker

        response = client.get(f"/brokers/{broker_id}/holdings", headers=auth_headers)
        assert response.status_code == 200

    def test_get_holdings_broker_not_found(self, client, auth_headers):
        """Test getting holdings from non-existent broker."""
        response = client.get("/brokers/99999/holdings", headers=auth_headers)
        assert response.status_code == 404


class TestBrokerCredentials:
    """Test credential handling and masking."""

    def test_credentials_masked_on_response(self, client, auth_headers):
        """Test that credentials are masked when returned."""
        response = client.post(
            "/brokers/",
            headers=auth_headers,
            json={
                "broker_name": "Zerodha",
                "credentials": {
                    "api_key": "my_super_secret_key_12345",
                    "access_token": "my_access_token_xyz"
                }
            }
        )

        data = response.json()
        api_key = data["credentials"]["api_key"]

        # Should not be full key
        assert api_key != "my_super_secret_key_12345"
        # Should be masked
        assert "***" in api_key or "*" in api_key