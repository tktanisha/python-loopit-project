import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.order import router
from setup.order_service_dependencies import get_order_service
from setup.product_dependencies import get_product_service


@pytest.fixture
def app():
    app = FastAPI()

    # mock jwt dependency
    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "user"}

    order_service = MagicMock()
    order_service.get_order_history = AsyncMock()
    order_service.mark_order_as_returned = AsyncMock()
    order_service.get_lender_orders = AsyncMock()

    product_service = MagicMock()
    product_service.get_product_by_id = AsyncMock()

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_order_service] = lambda: order_service
    app.dependency_overrides[get_product_service] = lambda: product_service

    app.include_router(router)

    # store refs for assertions
    app.state.order_service = order_service
    app.state.product_service = product_service

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_get_order_history_success(client, app):
    mock_order = MagicMock()
    mock_order.product_id = 10
    mock_order.model_dump.return_value = {"id": 1, "status": "returned"}

    app.state.order_service.get_order_history.return_value = [mock_order]
    app.state.product_service.get_product_by_id.return_value = MagicMock(
        model_dump=lambda: {"id": 10, "name": "Phone"}
    )

    resp = client.get(
        ApiPaths.GET_ORDER_HISTORY,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True
    assert isinstance(resp.json()["data"], list)


def test_get_order_history_invalid_status(client):
    resp = client.get(
        ApiPaths.GET_ORDER_HISTORY + "?status=wrongstatus",
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_get_order_history_failure(client, app):
    app.state.order_service.get_order_history.side_effect = Exception("db error")

    resp = client.get(
        ApiPaths.GET_ORDER_HISTORY,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_mark_order_as_returned_success(client, app):
    resp = client.patch(
        ApiPaths.RETURN_ORDER.format(orderId=1),
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    app.state.order_service.mark_order_as_returned.assert_awaited_once()


def test_mark_order_as_returned_failure(client, app):
    app.state.order_service.mark_order_as_returned.side_effect = Exception("fail")

    resp = client.patch(
        ApiPaths.RETURN_ORDER.format(orderId=1),
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_get_lender_orders_success(client, app):
    mock_order = MagicMock()
    mock_order.product_id = 5
    mock_order.model_dump.return_value = {"id": 1}

    app.state.order_service.get_lender_orders.return_value = [mock_order]
    app.state.product_service.get_product_by_id.return_value = MagicMock(
        model_dump=lambda: {"id": 5, "name": "Laptop"}
    )

    resp = client.get(
        ApiPaths.GET_LENDER_ORDERS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True
    assert isinstance(resp.json()["data"], list)


def test_get_lender_orders_failure(client, app):
    app.state.order_service.get_lender_orders.side_effect = Exception("err")

    resp = client.get(
        ApiPaths.GET_LENDER_ORDERS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False
