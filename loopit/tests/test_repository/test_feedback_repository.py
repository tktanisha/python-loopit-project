import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions
from datetime import datetime

from repository.feedback_repository import FeedbackRepo
from models.feedback import Feedback


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr(
        "repository.feedback_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return FeedbackRepo(dynamodb=dynamodb)


@pytest.mark.asyncio
async def test_create_feedback_success(repo, dynamodb):
    feedback = MagicMock(spec=Feedback)
    feedback.id = None
    feedback.given_by = 1
    feedback.given_to = 2
    feedback.text = "good"
    feedback.rating = 5
    feedback.created_at = datetime(2024, 1, 1)

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create_feedback(feedback)

    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_create_feedback_client_error(repo, dynamodb):
    feedback = MagicMock(spec=Feedback)
    feedback.id = 1
    feedback.given_by = 1
    feedback.given_to = 2
    feedback.text = "bad"
    feedback.rating = 2
    feedback.created_at = datetime(2024, 1, 1)

    dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "PutItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create_feedback(feedback)


@pytest.mark.asyncio
async def test_get_all_feedbacks_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "GivenBy": {"N": "1"},
                "GivenTo": {"N": "2"},
                "Text": {"S": "great"},
                "Rating": {"N": "5"},
                "CreatedAt": {"S": "2024-01-01T00:00:00"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        feedbacks = await repo.get_all_feedbacks()

    assert len(feedbacks) == 1
    fb = feedbacks[0]
    assert fb.id == 1
    assert fb.given_by == 1
    assert fb.given_to == 2
    assert fb.text == "great"
    assert fb.rating == 5


@pytest.mark.asyncio
async def test_get_all_feedbacks_client_error(repo, dynamodb):
    dynamodb.query.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "Query",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.get_all_feedbacks()


@pytest.mark.asyncio
async def test_save_no_op(repo):
    await repo.save()
