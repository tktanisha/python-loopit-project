import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.buy_request import router
from setup.buy_request_dependencies import get_buyer_request_service
from setup.product_dependencies import get_product_service


@pytest.fixture
def app(buyer_request_service, product_service):
    app = FastAPI()

    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "buyer"}

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_buyer_request_service] = lambda: buyer_request_service
    app.dependency_overrides[get_product_service] = lambda: product_service

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def buyer_request_service():
    svc = MagicMock()
    svc.create_buyer_request = AsyncMock()
    svc.get_all_buyer_requests = AsyncMock()
    svc.update_buyer_request_status = AsyncMock()
    return svc


@pytest.fixture
def product_service():
    svc = MagicMock()
    svc.get_product_by_id = AsyncMock()
    return svc


def test_create_buyer_request_success(client, buyer_request_service):
    payload = {
        "product_id": 10
    }

    resp = client.post(
        ApiPaths.CREATE_BUYER_REQUEST,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 201
    buyer_request_service.create_buyer_request.assert_awaited_once()


def test_create_buyer_request_failure(client, buyer_request_service):
    buyer_request_service.create_buyer_request.side_effect = Exception("error")

    payload = {
        "product_id": 10
    }

    resp = client.post(
        ApiPaths.CREATE_BUYER_REQUEST,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_get_all_buyer_requests_success(client, buyer_request_service, product_service):
    mock_request = MagicMock()
    mock_request.product_id = 1
    mock_request.model_dump.return_value = {"id": 1, "product_id": 10}

    buyer_request_service.get_all_buyer_requests.return_value = [mock_request]
    product_service.get_product_by_id.return_value = MagicMock(
        model_dump=lambda: {"id": 10, "name": "Phone"}
    )

    resp = client.get(
        ApiPaths.GET_BUYER_REQUESTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert "buy_request" in data[0]
    assert "product" in data[0]


def test_get_all_buyer_requests_failure(client, buyer_request_service):
    buyer_request_service.get_all_buyer_requests.side_effect = Exception("err")

    resp = client.get(
        ApiPaths.GET_BUYER_REQUESTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_update_buyer_request_status_success(client, buyer_request_service):
    payload = {
        "status": "Approved"
    }

    resp = client.patch(
        ApiPaths.UPDATE_BUYER_REQUEST_STATUS.format(requestId=1),
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    buyer_request_service.update_buyer_request_status.assert_awaited_once()


def test_update_buyer_request_status_failure(client, buyer_request_service):
    buyer_request_service.update_buyer_request_status.side_effect = Exception("bad")

    payload = {
        "status": "Approved"
    }

    resp = client.patch(
        ApiPaths.UPDATE_BUYER_REQUEST_STATUS.format(requestId=1),
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False
