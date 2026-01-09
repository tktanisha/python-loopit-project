import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.product import router
from setup.product_dependencies import get_product_service


@pytest.fixture
def app():
    app = FastAPI()

    # mock jwt dependency
    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "lender"}

    mock_service = MagicMock()
    mock_service.get_all_products = AsyncMock()
    mock_service.get_product_by_id = AsyncMock()
    mock_service.create_product = AsyncMock()
    mock_service.update_product = AsyncMock()
    mock_service.delete_product = AsyncMock()

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_product_service] = lambda: mock_service

    app.include_router(router)
    app.state.product_service = mock_service
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_get_all_products_success(client, app):
    app.state.product_service.get_all_products.return_value = [
        {"id": 1, "name": "Phone"}
    ]

    resp = client.get(
        ApiPaths.GET_PRODUCTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True
    assert isinstance(resp.json()["data"], list)


def test_get_all_products_failure(client, app):
    app.state.product_service.get_all_products.side_effect = Exception("db error")

    resp = client.get(
        ApiPaths.GET_PRODUCTS,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_get_product_by_id_success(client, app):
    app.state.product_service.get_product_by_id.return_value = {
        "id": 1,
        "name": "Laptop"
    }

    resp = client.get(
        ApiPaths.GET_PRODUCT_BY_ID.format(id=1),
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True


def test_get_product_by_id_not_found(client, app):
    app.state.product_service.get_product_by_id.side_effect = Exception("not found")

    resp = client.get(
        ApiPaths.GET_PRODUCT_BY_ID.format(id=99),
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 404
    assert resp.json()["status"] is False


def test_create_product_success(client, app):
    payload = {
        "name": "Phone",
        "description": "Nice",
        "category_id": 1,
        "duration": 10,
        "is_available": True,
        "image_url": ""
    }

    resp = client.post(
        ApiPaths.CREATE_PRODUCT,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 201
    app.state.product_service.create_product.assert_awaited_once()


def test_create_product_forbidden(client, app):
    # override role to non-lender
    async def mock_verify_jwt_buyer(request: Request):
        request.state.user = {"user_id": 1, "role": "buyer"}

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt_buyer

    payload = {
        "name": "Phone",
        "description": "Nice",
        "category_id": 1,
        "duration": 10,
        "is_available": True,
        "image_url": ""
    }

    resp = client.post(
        ApiPaths.CREATE_PRODUCT,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 403
    assert resp.json()["status"] is False


def test_update_product_success(client, app):
    payload = {
        "name": "Updated",
        "description": "Updated desc",
        "category_id": 2,
        "duration": 5,
        "is_available": False,
        "image_url": ""
    }

    resp = client.put(
        ApiPaths.UPDATE_PRODUCT.format(id=1),
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    app.state.product_service.update_product.assert_awaited_once()


def test_delete_product_success(client, app):
    resp = client.delete(
        ApiPaths.DELETE_PRODUCT.format(id=1),
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 200
    app.state.product_service.delete_product.assert_awaited_once()
