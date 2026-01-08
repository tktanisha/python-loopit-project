import pytest
from fastapi.testclient import TestClient
from ...app import app
from loopit.src.helpers.auth_helper import AuthHelper
from loopit.src.test.override_dependency.verify_auth import override_verify_jwt

#routes testing is to just check if endpoints are hit or not

@pytest.fixture
def client():
    app.dependency_overrides[AuthHelper.verify_jwt] = override_verify_jwt()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_category_route(client,mocker):
    mock_service = mocker.AsyncMock()

    mocker.patch(
        "setup.category_dependecies.get_catgeory_service",
        return_value = mock_service
    )

    response = client.post(
        "/category",
        json ={
            "name":"Books",
            "price":100,
            "security":10
        },
    )

    assert response.status_code == 201
    