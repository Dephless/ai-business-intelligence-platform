import pytest

from app.core.config import settings
from app.core.security import decode_access_token


@pytest.fixture(autouse=True)
def configure_test_secret(monkeypatch):
    """Provide a dedicated JWT secret for API tests."""
    monkeypatch.setattr(
        settings,
        "secret_key",
        "test-secret-key-for-unit-tests-32-bytes",
    )


def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "analyst@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


def test_register_user_normalizes_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ANALYST@EXAMPLE.COM",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "analyst@example.com"


def test_register_user_rejects_duplicate_email(client):
    payload = {
        "email": "analyst@example.com",
        "password": "secure-password-123",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_user_rejects_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 422


def test_register_user_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_user_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "password": "secure-password-123",
        },
    )

    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "analyst@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data

    token_payload = decode_access_token(data["access_token"])
    assert token_payload["sub"] == "1"


def test_login_user_rejects_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "password": "secure-password-123",
        },
    )

    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "analyst@example.com",
            "password": "wrong-password-123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_login_user_rejects_unknown_email(client):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "unknown@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 401
