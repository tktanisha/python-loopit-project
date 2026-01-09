import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.user import router
from setup.user_dependencies import get_user_service


@pytest.fixture
def user_service():
    svc = MagicMock()
    svc.become_lender = AsyncMock()
    svc.get_all_users = AsyncMock()
    svc.get_user_by_id = AsyncMock()
    svc.delete_user_by_id = AsyncMock()
    return svc


@pytest.fixture
def app(user_service):
    app = FastAPI()

    async def mock_verify_jwt(request: Request):
        # admin user by default
        request.state.user = {"user_id": 1, "role": "admin"}

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_user_service] = lambda: user_service

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_become_lender_success(client, user_service):
    resp = client.patch(
        ApiPaths.BECOME_LENDER,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    user_service.become_lender.assert_awaited_once()


def test_become_lender_failure(client, user_service):
    user_service.become_lender.side_effect = Exception("error")

    resp = client.patch(
        ApiPaths.BECOME_LENDER,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_get_all_users_success(client, user_service):
    user_service.get_all_users.return_value = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
    ]

    resp = client.get(
        ApiPaths.GET_USERS,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True
    assert isinstance(resp.json()["data"], list)


def test_get_all_users_forbidden(client, user_service, app):
    # override JWT to simulate non-admin
    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 2, "role": "buyer"}

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt

    resp = client.get(
        ApiPaths.GET_USERS,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 403
    assert resp.json()["status"] is False


def test_get_user_by_id_success(client, user_service):
    user_service.get_user_by_id.return_value = {
        "id": 1,
        "name": "John",
    }

    resp = client.get(
        ApiPaths.GET_USER_BY_ID.format(id=1),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True


def test_get_user_by_id_not_found(client, user_service):
    user_service.get_user_by_id.return_value = None

    resp = client.get(
        ApiPaths.GET_USER_BY_ID.format(id=99),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 404
    assert resp.json()["status"] is False


def test_delete_user_success(client, user_service):
    resp = client.delete(
        ApiPaths.DELETE_USER_BY_ID.format(id=1),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    user_service.delete_user_by_id.assert_awaited_once()


def test_delete_user_failure(client, user_service):
    user_service.delete_user_by_id.side_effect = Exception("err")

    resp = client.delete(
        ApiPaths.DELETE_USER_BY_ID.format(id=1),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False
