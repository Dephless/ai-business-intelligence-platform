from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_is_hashed():
    password = "SecurePassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_wrong_password_is_rejected():
    hashed_password = hash_password("CorrectPassword123!")

    assert not verify_password("WrongPassword123!", hashed_password)


def test_access_token_contains_subject(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "test-secret-key-for-unit-tests-32-bytes")

    token = create_access_token({"sub": "123"})

    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert "exp" in payload


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "test-secret-key-for-unit-tests-32-bytes")

    token = create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_token_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "test-secret-key-for-unit-tests-32-bytes")

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid.token.value")


def test_token_creation_requires_secret_key(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", None)

    with pytest.raises(RuntimeError, match="JWT secret key"):
        create_access_token({"sub": "123"})
