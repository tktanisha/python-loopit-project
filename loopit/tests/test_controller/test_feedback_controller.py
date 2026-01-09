import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.feedback_controller import (
    give_feedback,
    get_all_given_feedbacks,
    get_all_received_feedbacks,
)
from schemas.feedback import FeedbackRequest


@pytest.mark.asyncio
async def test_give_feedback_success():
    service = MagicMock()
    service.give_feedback = AsyncMock(return_value=None)

    feedback = FeedbackRequest(
        order_id=1,
        feedback_text="good product",
        rating=4,
    )

    user_ctx = {"user_id": 10}

    resp = await give_feedback(feedback, service, user_ctx)

    service.give_feedback.assert_awaited_once()
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_give_feedback_failure():
    service = MagicMock()
    service.give_feedback = AsyncMock(side_effect=Exception("something failed"))

    feedback = FeedbackRequest(
        order_id=1,
        feedback_text="bad",
        rating=1,
    )

    user_ctx = {"user_id": 10}

    resp = await give_feedback(feedback, service, user_ctx)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_all_given_feedbacks_success():
    service = MagicMock()
    service.get_all_given_feedbacks = AsyncMock(
        return_value=[
            {"id": 1, "text": "nice"},
            {"id": 2, "text": "ok"},
        ]
    )

    user_ctx = {"user_id": 5}

    resp = await get_all_given_feedbacks(service, user_ctx)

    service.get_all_given_feedbacks.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_given_feedbacks_failure():
    service = MagicMock()
    service.get_all_given_feedbacks = AsyncMock(side_effect=Exception("db down"))

    user_ctx = {"user_id": 5}

    resp = await get_all_given_feedbacks(service, user_ctx)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_all_received_feedbacks_success():
    service = MagicMock()
    service.get_all_received_feedbacks = AsyncMock(
        return_value=[
            {"id": 3, "text": "great"},
        ]
    )

    user_ctx = {"user_id": 7}

    resp = await get_all_received_feedbacks(service, user_ctx)

    service.get_all_received_feedbacks.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_received_feedbacks_failure():
    service = MagicMock()
    service.get_all_received_feedbacks = AsyncMock(side_effect=Exception("error"))

    user_ctx = {"user_id": 7}

    resp = await get_all_received_feedbacks(service, user_ctx)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
