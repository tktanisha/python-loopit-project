import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from controller.auth_controller import login_controller, signup_controller
from api.v1.routes.auth import router
from setup.dependencies import get_auth_service
from exception.user import UserAlreadyExistsError, InvalidCredentialsError, AuthServiceError


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_service_mock():
    service = MagicMock()
    service.register = AsyncMock(return_value=None)
    service.login = AsyncMock(
        return_value=("mock-token", MagicMock(
            id=1,
            full_name="John",
            role=MagicMock(value="user"),
        ))
    )
    return service


def override_auth_service(auth_service_mock):
    return auth_service_mock


def test_signup_success(app, client, auth_service_mock):
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "fullname": "John Doe",
        "email": "a@b.com",
        "phone_number": "123456",
        "address": "addr",
        "password": "secret",
        "society_id": 1,
    }

    resp = client.post("/auth/register", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert "token" in body
    assert body["user"]["name"] == "John"


def test_signup_user_already_exists(app, client, auth_service_mock):
    auth_service_mock.register.side_effect = UserAlreadyExistsError("exists")
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "fullname": "John Doe",
        "email": "a@b.com",
        "phone_number": "123456",
        "address": "addr",
        "password": "secret",
        "society_id": 1,
    }

    resp = client.post("/auth/register", json=payload)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "User already exists"


def test_signup_register_failure(app, client, auth_service_mock):
    auth_service_mock.register.side_effect = AuthServiceError("db down")
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "fullname": "John Doe",
        "email": "a@b.com",
        "phone_number": "123456",
        "address": "addr",
        "password": "secret",
        "society_id": 1,
    }

    resp = client.post("/auth/register", json=payload)

    assert resp.status_code == 500


def test_login_success(app, client, auth_service_mock):
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "email": "a@b.com",
        "password": "secret",
    }

    resp = client.post("/auth/login", json=payload)

    assert resp.status_code == 200
    assert resp.json()["token"] == "mock-token"


def test_login_invalid_credentials(app, client, auth_service_mock):
    auth_service_mock.login.side_effect = InvalidCredentialsError("bad creds")
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "email": "a@b.com",
        "password": "wrong",
    }

    resp = client.post("/auth/login", json=payload)

    assert resp.status_code == 401


def test_login_service_error(app, client, auth_service_mock):
    auth_service_mock.login.side_effect = AuthServiceError("error")
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock

    payload = {
        "email": "a@b.com",
        "password": "secret",
    }

    resp = client.post("/auth/login", json=payload)

    assert resp.status_code == 500
