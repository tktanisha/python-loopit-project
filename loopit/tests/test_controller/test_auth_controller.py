import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from controller.auth_controller import signup_controller, login_controller
from schemas.auth import RegisterRequest
from models.user import User
from exception.user import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    AuthServiceError,
)
from models.enums.user import Role


@pytest.mark.asyncio
async def test_signup_controller_success():
    payload = RegisterRequest(
        fullname="John Doe",
        email="john@test.com",
        phone_number="123456",
        address="addr",
        password="pass123",
        society_id=1,
    )

    auth_service = MagicMock()
    auth_service.register = AsyncMock(return_value=None)

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.full_name = "John Doe"
    mock_user.role = Role.user

    auth_service.login = AsyncMock(return_value=("token123", mock_user))

    resp = await signup_controller(payload, auth_service)

    assert resp["token"] == "token123"
    assert resp["user"]["id"] == 1
    assert resp["user"]["name"] == "John Doe"


@pytest.mark.asyncio
async def test_signup_controller_user_already_exists():
    payload = RegisterRequest(
        fullname="John Doe",
        email="john@test.com",
        phone_number="123",
        address=None,
        password="pass",
        society_id=1,
    )

    auth_service = MagicMock()
    auth_service.register = AsyncMock(side_effect=UserAlreadyExistsError())

    with pytest.raises(HTTPException) as exc:
        await signup_controller(payload, auth_service)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_signup_controller_register_failure():
    payload = RegisterRequest(
        fullname="John",
        email="john@test.com",
        phone_number="123",
        address=None,
        password="pass",
        society_id=1,
    )

    auth_service = MagicMock()
    auth_service.register = AsyncMock(side_effect=AuthServiceError("err"))

    with pytest.raises(HTTPException) as exc:
        await signup_controller(payload, auth_service)

    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_signup_controller_login_invalid_credentials():
    payload = RegisterRequest(
        fullname="John",
        email="john@test.com",
        phone_number="123",
        address=None,
        password="pass",
        society_id=1,
    )

    auth_service = MagicMock()
    auth_service.register = AsyncMock(return_value=None)
    auth_service.login = AsyncMock(side_effect=InvalidCredentialsError())

    with pytest.raises(HTTPException) as exc:
        await signup_controller(payload, auth_service)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_controller_success():
    auth_service = MagicMock()

    mock_user = MagicMock(spec=User)
    mock_user.id = 10
    mock_user.full_name = "Jane"
    mock_user.role = Role.user

    auth_service.login = AsyncMock(return_value=("tok", mock_user))

    resp = await login_controller("a@b.com", "pass", auth_service)

    assert resp["token"] == "tok"
    assert resp["user"]["id"] == 10
    assert resp["user"]["name"] == "Jane"


@pytest.mark.asyncio
async def test_login_controller_invalid_credentials():
    auth_service = MagicMock()
    auth_service.login = AsyncMock(side_effect=InvalidCredentialsError())

    with pytest.raises(HTTPException) as exc:
        await login_controller("a@b.com", "pass", auth_service)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_controller_service_error():
    auth_service = MagicMock()
    auth_service.login = AsyncMock(side_effect=AuthServiceError("error"))

    with pytest.raises(HTTPException) as exc:
        await login_controller("a@b.com", "pass", auth_service)

    assert exc.value.status_code == 500
