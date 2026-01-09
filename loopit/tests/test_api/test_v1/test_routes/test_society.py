import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from api.v1.routes.society import router
from setup.society_dependency import get_society_service


@pytest.fixture
def app():
    app = FastAPI()

    mock_service = MagicMock()
    mock_service.create_society = AsyncMock()
    mock_service.get_all_societies = AsyncMock()
    mock_service.update_society = AsyncMock()
    mock_service.delete_society = AsyncMock()

    app.dependency_overrides[get_society_service] = lambda: mock_service
    app.include_router(router)

    app.state.mock_service = mock_service
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_create_society_success(client, app):
    payload = {
        "name": "My Society",
        "location": "Bangalore",
        "pincode": "560001",
    }

    resp = client.post(
        ApiPaths.CREATE_SOCIETY,
        json=payload,
    )

    assert resp.status_code == 201
    app.state.mock_service.create_society.assert_awaited_once()


def test_create_society_failure(client, app):
    app.state.mock_service.create_society.side_effect = Exception("error")

    payload = {
        "name": "Fail Society",
        "location": "Delhi",
        "pincode": "110001",
    }

    resp = client.post(
        ApiPaths.CREATE_SOCIETY,
        json=payload,
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False


def test_get_all_society_success(client, app):
    app.state.mock_service.get_all_societies.return_value = [
        {"id": 1, "name": "Soc1"},
        {"id": 2, "name": "Soc2"},
    ]

    resp = client.get(ApiPaths.GET_SOCIETY)

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_all_society_failure(client, app):
    app.state.mock_service.get_all_societies.side_effect = Exception("db error")

    resp = client.get(ApiPaths.GET_SOCIETY)

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_update_society_success(client, app):
    payload = {
        "name": "Updated Society",
        "location": "Mumbai",
        "pincode": "400001",
    }

    resp = client.put(
        ApiPaths.UPDATE_SOCIETY.format(id=1),
        json=payload,
    )

    assert resp.status_code == 205
    app.state.mock_service.update_society.assert_awaited_once()


def test_update_society_failure(client, app):
    app.state.mock_service.update_society.side_effect = Exception("update failed")

    payload = {
        "name": "Bad Update",
        "location": "Chennai",
        "pincode": "600001",
    }

    resp = client.put(
        ApiPaths.UPDATE_SOCIETY.format(id=1),
        json=payload,
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False


def test_delete_society_success(client, app):
    resp = client.delete(
        ApiPaths.DELETE_SOCIETY.format(id=1),
    )

    assert resp.status_code == 200
    app.state.mock_service.delete_society.assert_awaited_once()


def test_delete_society_failure(client, app):
    app.state.mock_service.delete_society.side_effect = Exception("delete failed")

    resp = client.delete(
        ApiPaths.DELETE_SOCIETY.format(id=1),
    )

    assert resp.status_code == 500
    assert resp.json()["status"] is False
