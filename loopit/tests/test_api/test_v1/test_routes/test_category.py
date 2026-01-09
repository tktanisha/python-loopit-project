import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.category import router
from setup.category_dependency import get_category_service


@pytest.fixture
def category_service():
    svc = MagicMock()
    svc.create_category = AsyncMock()
    svc.get_all_categories = AsyncMock()
    svc.update_category = AsyncMock()
    svc.delete_category = AsyncMock()
    return svc


@pytest.fixture
def app(category_service):
    app = FastAPI()

    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "admin"}

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_category_service] = lambda: category_service

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_create_category_success(client, category_service):
    payload = {
        "name": "Electronics",
        "price": 100,
        "security": 20,
    }

    resp = client.post(
        ApiPaths.CREATE_CATEGORY,
        json=payload,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 201
    category_service.create_category.assert_awaited_once()


def test_create_category_failure(client, category_service):
    category_service.create_category.side_effect = Exception("error")

    payload = {
        "name": "Electronics",
        "price": 100,
        "security": 20,
    }

    resp = client.post(
        ApiPaths.CREATE_CATEGORY,
        json=payload,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_get_all_category_success(client, category_service):
    category_service.get_all_categories.return_value = [
        {"id": 1, "name": "Electronics"}
    ]

    resp = client.get(
        ApiPaths.GET_CATEGORY,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] is True
    assert isinstance(resp.json()["data"], list)


def test_get_all_category_failure(client, category_service):
    category_service.get_all_categories.side_effect = Exception("err")

    resp = client.get(
        ApiPaths.GET_CATEGORY,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_update_category_success(client, category_service):
    payload = {
        "name": "Updated",
        "price": 200,
        "security": 50,
    }

    resp = client.put(
        ApiPaths.UPDATE_CATEGORY.format(id=1),
        json=payload,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 205
    category_service.update_category.assert_awaited_once()


def test_update_category_failure(client, category_service):
    category_service.update_category.side_effect = Exception("fail")

    payload = {
        "name": "Updated",
        "price": 200,
        "security": 50,
    }

    resp = client.put(
        ApiPaths.UPDATE_CATEGORY.format(id=1),
        json=payload,
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_delete_category_success(client, category_service):
    resp = client.delete(
        ApiPaths.DELETE_CATEGORY.format(id=1),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 200
    category_service.delete_category.assert_awaited_once()


def test_delete_category_failure(client, category_service):
    category_service.delete_category.side_effect = Exception("nope")

    resp = client.delete(
        ApiPaths.DELETE_CATEGORY.format(id=1),
        headers={"Authorization": "Bearer test"},
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False
