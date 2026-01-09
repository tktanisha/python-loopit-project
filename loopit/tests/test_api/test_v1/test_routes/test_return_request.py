import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.return_request import router
from setup.return_request_service import get_return_request_service


@pytest.fixture
def app():
    app = FastAPI()

    # mock jwt
    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "buyer"}

    mock_service = MagicMock()
    mock_service.get_pending_return_requests = AsyncMock()
    mock_service.create_return_request = AsyncMock()
    mock_service.update_return_request_status = AsyncMock()

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_return_request_service] = lambda: mock_service

    app.include_router(router)
    app.state.mock_service = mock_service
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_get_return_requests_success(client, app):
    app.state.mock_service.get_pending_return_requests.return_value = [
        MagicMock(model_dump=lambda: {"id": 1, "order_id": 10})
    ]

    resp = client.get(
        ApiPaths.GET_RETURN_REQUESTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True


def test_get_return_requests_failure(client, app):
    app.state.mock_service.get_pending_return_requests.side_effect = Exception("db error")

    resp = client.get(
        ApiPaths.GET_RETURN_REQUESTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_create_return_request_success(client, app):
    payload = {
        "order_id": 123
    }

    resp = client.post(
        ApiPaths.CREATE_RETURN_REQUEST,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 201
    app.state.mock_service.create_return_request.assert_awaited_once()


def test_create_return_request_failure(client, app):
    app.state.mock_service.create_return_request.side_effect = Exception("error")

    payload = {
        "order_id": 123
    }

    resp = client.post(
        ApiPaths.CREATE_RETURN_REQUEST,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_update_return_request_status_success(client, app):
    payload = {
        "status": "Approved"
    }

    resp = client.patch(
        ApiPaths.UPDATE_RETURN_REQUEST_STATUS.format(requestId=1),
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    app.state.mock_service.update_return_request_status.assert_awaited_once()


def test_update_return_request_status_failure(client, app):
    app.state.mock_service.update_return_request_status.side_effect = Exception("bad")

    payload = {
        "status": "Approved"
    }

    resp = client.patch(
        ApiPaths.UPDATE_RETURN_REQUEST_STATUS.format(requestId=1),
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False
