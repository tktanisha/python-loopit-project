import pytest
from unittest.mock import AsyncMock, MagicMock

from service.feedback_service import FeedbackService
from models.feedback import Feedback


@pytest.fixture
def feedback_repo():
    return AsyncMock()


@pytest.fixture
def product_repo():
    return AsyncMock()


@pytest.fixture
def order_repo():
    return AsyncMock()


@pytest.fixture
def service(feedback_repo, product_repo, order_repo):
    return FeedbackService(
        feedback_repo=feedback_repo,
        product_repo=product_repo,
        order_repo=order_repo,
    )


@pytest.mark.asyncio
async def test_give_feedback_success(service, feedback_repo, product_repo, order_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=10)
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=99)
    )

    user_ctx = {"user_id": 1}

    await service.give_feedback(
        order_id=5,
        feedback_text="great",
        rating=5,
        user_ctx=user_ctx,
    )

    feedback_repo.create_feedback.assert_called_once()
    feedback = feedback_repo.create_feedback.call_args[0][0]
    assert isinstance(feedback, Feedback)
    assert feedback.given_by == 1
    assert feedback.given_to == 99
    assert feedback.rating == 5
    assert feedback.text == "great"


@pytest.mark.asyncio
async def test_give_feedback_invalid_user(service):
    with pytest.raises(RuntimeError):
        await service.give_feedback(1, "text", 5, {"user_id": 0})


@pytest.mark.asyncio
async def test_give_feedback_order_not_found(service, order_repo):
    order_repo.get_order_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.give_feedback(1, "text", 5, {"user_id": 1})


@pytest.mark.asyncio
async def test_give_feedback_product_not_found(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=10)
    product_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.give_feedback(1, "text", 5, {"user_id": 1})


@pytest.mark.asyncio
async def test_give_feedback_to_self(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=10)
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=1)
    )
    with pytest.raises(RuntimeError):
        await service.give_feedback(1, "text", 5, {"user_id": 1})


@pytest.mark.asyncio
async def test_get_all_given_feedbacks_success(service, feedback_repo):
    feedback_repo.get_all_feedbacks.return_value = [
        MagicMock(given_by=1),
        MagicMock(given_by=2),
        MagicMock(given_by=1),
    ]

    result = await service.get_all_given_feedbacks({"user_id": 1})

    assert len(result) == 2
    assert all(int(f.given_by) == 1 for f in result)


@pytest.mark.asyncio
async def test_get_all_given_feedbacks_invalid_user(service):
    with pytest.raises(RuntimeError):
        await service.get_all_given_feedbacks({"user_id": -1})


@pytest.mark.asyncio
async def test_get_all_received_feedbacks_success(service, feedback_repo):
    feedback_repo.get_all_feedbacks.return_value = [
        MagicMock(given_to=1),
        MagicMock(given_to=2),
        MagicMock(given_to=1),
    ]

    result = await service.get_all_received_feedbacks({"user_id": 1})

    assert len(result) == 2
    assert all(int(f.given_to) == 1 for f in result)


@pytest.mark.asyncio
async def test_get_all_received_feedbacks_invalid_user(service):
    with pytest.raises(RuntimeError):
        await service.get_all_received_feedbacks({"user_id": None})
