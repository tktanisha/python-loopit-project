import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from helpers.api_paths import ApiPaths
from helpers.auth_helper import AuthHelper
from api.v1.routes.feedback import router
from setup.feedback_dependencies import get_feedback_service


@pytest.fixture
def app():
    app = FastAPI()

    # mock jwt verification
    async def mock_verify_jwt(request: Request):
        request.state.user = {"user_id": 1, "role": "user"}

    feedback_service = MagicMock()
    feedback_service.give_feedback = AsyncMock()

    app.dependency_overrides[AuthHelper.verify_jwt] = mock_verify_jwt
    app.dependency_overrides[get_feedback_service] = lambda: feedback_service

    app.include_router(router)

    # keep reference for assertions
    app.state.feedback_service = feedback_service

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_give_feedback_success(client, app):
    payload = {
        "order_id": 1,
        "feedback_text": "good product",
        "rating": 5,
    }

    resp = client.post(
        ApiPaths.CREATE_FEEDBACK,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 201
    assert resp.json()["status"] is True
    app.state.feedback_service.give_feedback.assert_awaited_once()


def test_give_feedback_failure(client, app):
    app.state.feedback_service.give_feedback.side_effect = Exception("failed")

    payload = {
        "order_id": 1,
        "feedback_text": "bad product",
        "rating": 1,
    }

    resp = client.post(
        ApiPaths.CREATE_FEEDBACK,
        json=payload,
        headers={"Authorization": "Bearer mocktoken"},
    )

    assert resp.status_code == 400
    assert resp.json()["status"] is False
