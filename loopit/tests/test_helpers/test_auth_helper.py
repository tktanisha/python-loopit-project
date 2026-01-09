import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import jwt
from unittest.mock import MagicMock

from helpers.auth_helper import AuthHelper
from helpers.app_settings import AppSettings


def test_hash_password_success():
    password = "secret123"
    hashed = AuthHelper.hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password


def test_verify_password_success():
    password = "secret123"
    hashed = AuthHelper.hash_password(password)

    assert AuthHelper.verify_password(password, hashed) is True


def test_verify_password_failure():
    password = "secret123"
    hashed = AuthHelper.hash_password(password)

    assert AuthHelper.verify_password("wrong", hashed) is False


def test_create_token_success(monkeypatch):
    monkeypatch.setattr(AppSettings, "JWT_SECRET_KEY", "secret")
    monkeypatch.setattr(AppSettings, "JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(AppSettings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15)

    token = AuthHelper.create_token(user_id=1, role="user")

    decoded = jwt.decode(
        token,
        "secret",
        algorithms=["HS256"],
    )

    assert decoded["user_id"] == "1"
    assert decoded["role"] == "user"
    assert "exp" in decoded
    assert "iat" in decoded


def test_verify_jwt_success(monkeypatch):
    monkeypatch.setattr(AppSettings, "JWT_SECRET_KEY", "secret")
    monkeypatch.setattr(AppSettings, "JWT_ALGORITHM", "HS256")

    payload = {
        "user_id": "1",
        "role": "user",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
    }

    token = jwt.encode(payload, "secret", algorithm="HS256")

    request = MagicMock()
    request.headers = {"Authorization": f"Bearer {token}"}
    request.state = MagicMock()

    AuthHelper.verify_jwt(request)

    assert request.state.user["user_id"] == "1"
    assert request.state.user["role"] == "user"


def test_verify_jwt_missing_header():
    request = MagicMock()
    request.headers = {}

    with pytest.raises(HTTPException) as exc:
        AuthHelper.verify_jwt(request)

    assert exc.value.status_code == 401


def test_verify_jwt_invalid_token(monkeypatch):
    monkeypatch.setattr(AppSettings, "JWT_SECRET_KEY", "secret")
    monkeypatch.setattr(AppSettings, "JWT_ALGORITHM", "HS256")

    request = MagicMock()
    request.headers = {"Authorization": "Bearer invalid.token.value"}

    with pytest.raises(HTTPException) as exc:
        AuthHelper.verify_jwt(request)

    assert exc.value.status_code == 401


def test_verify_jwt_expired_token(monkeypatch):
    monkeypatch.setattr(AppSettings, "JWT_SECRET_KEY", "secret")
    monkeypatch.setattr(AppSettings, "JWT_ALGORITHM", "HS256")

    payload = {
        "user_id": "1",
        "role": "user",
        "iat": int((datetime.now(timezone.utc) - timedelta(minutes=10)).timestamp()),
        "exp": int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp()),
    }

    token = jwt.encode(payload, "secret", algorithm="HS256")

    request = MagicMock()
    request.headers = {"Authorization": f"Bearer {token}"}

    with pytest.raises(HTTPException) as exc:
        AuthHelper.verify_jwt(request)

    assert exc.value.status_code == 401
