"""
Authentication API Tests

Tests for /auth endpoints: login, register, profile, password management.
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
        assert "user_id" in data
        assert "username" in data

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username fails."""
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/auth/register",
            json={
                "username": "differentuser",
                "email": "test@example.com",  # Already exists
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "username_or_email": "testuser",
                "password": "TestPass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"

    def test_login_with_email(self, client, test_user):
        """Test login using email instead of username."""
        response = client.post(
            "/auth/login",
            json={
                "username_or_email": "test@example.com",
                "password": "TestPass123"
            }
        )
        assert response.status_code == 200
        assert "token" in response.json()

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/auth/login",
            json={
                "username_or_email": "testuser",
                "password": "WrongPassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post(
            "/auth/login",
            json={
                "username_or_email": "nonexistent",
                "password": "TestPass123"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "Trader"

    def test_get_current_user_no_auth(self, client):
        """Test getting current user without auth fails."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        response = client.patch(
            "/auth/me",
            headers=auth_headers,
            json={"email": "updated@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert data["pending"]["email"] == "updated@example.com"

    def test_change_password(self, client, auth_headers, test_user):
        """Test changing password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPass123",
                "new_password": "NewSecurePass456"
            }
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password fails."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword",
                "new_password": "NewSecurePass456"
            }
        )
        assert response.status_code == 401

    def test_delete_account(self, client, auth_headers):
        """Test deleting own account."""
        response = client.delete("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Account deleted successfully"

        # Verify can't login after deletion
        login_response = client.post(
            "/auth/login",
            json={"username_or_email": "testuser", "password": "TestPass123"}
        )
        assert login_response.status_code == 401