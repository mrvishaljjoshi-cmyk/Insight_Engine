"""
Insight Engine - Pytest Configuration and Fixtures

This module provides shared fixtures for testing the Insight Engine API.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole, BrokerCredential


from app.core.limiter import limiter


# Test database URL (SQLite in-memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test function."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override."""
    limiter.enabled = False  # Disable rate limiting for tests

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        mobile_no="+919876543210",
        hashed_password=get_password_hash("TestPass123"),
        role=UserRole.Trader,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    """Create an admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123"),
        role=UserRole.Admin,
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/auth/login",
        json={"username_or_email": "testuser", "password": "TestPass123"}
    )
    if response.status_code != 200:
        pytest.fail(f"Login failed for testuser: {response.json()}")
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post(
        "/auth/login",
        json={"username_or_email": "admin", "password": "AdminPass123"}
    )
    if response.status_code != 200:
        pytest.fail(f"Login failed for admin: {response.json()}")
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}