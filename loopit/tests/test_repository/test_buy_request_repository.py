import pytest
from unittest.mock import MagicMock, patch
import botocore
from datetime import datetime, timezone

from repository.buy_request_repository import BuyRequestRepo
from models.buy_request import BuyingRequest
from models.enums.buy_request import BuyRequestStatus


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr("repository.buy_request_repository.settings.DDB_TABLE_NAME", "test-table")
    return BuyRequestRepo(dynamodb=dynamodb)


@pytest.mark.asyncio
async def test_create_buyer_request_success(repo, dynamodb):
    req = MagicMock(
        id=None,
        product_id=1,
        requested_by=2,
        status=BuyRequestStatus.Pending,
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create_buyer_request(req)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_create_buyer_request_client_error(repo, dynamodb):
    req = MagicMock(
        id=1,
        product_id=1,
        requested_by=2,
        status=BuyRequestStatus.Pending,
    )
    dynamodb.transact_write_items.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}}, "op"
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create_buyer_request(req)


@pytest.mark.asyncio
async def test_get_all_buyer_requests_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "ProductId": {"N": "10"},
                "RequestedBy": {"N": "5"},
                "Status": {"S": BuyRequestStatus.Pending.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        result = await repo.get_all_buyer_requests(
            product_id=10,
            filter_statuses=[BuyRequestStatus.Pending.value],
        )

    assert len(result) == 1
    assert result[0].requested_by == 5


@pytest.mark.asyncio
async def test_get_all_buyer_requests_client_error(repo, dynamodb):
    dynamodb.query.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}}, "op"
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.get_all_buyer_requests()


@pytest.mark.asyncio
async def test_update_status_buyer_request_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "Status": {"S": BuyRequestStatus.Pending.value},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.update_status_buyer_request(1, BuyRequestStatus.Approved.value)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_update_status_buyer_request_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.update_status_buyer_request(1, BuyRequestStatus.Approved.value)


@pytest.mark.asyncio
async def test_get_buyer_request_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "ProductId": {"N": "10"},
            "RequestedBy": {"N": "5"},
            "Status": {"S": BuyRequestStatus.Pending.value},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        req = await repo.get_buyer_request_by_id(1)

    assert req is not None
    assert req.id == 1


@pytest.mark.asyncio
async def test_get_buyer_request_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        req = await repo.get_buyer_request_by_id(1)

    assert req is None


@pytest.mark.asyncio
async def test_delete_buyer_request_success(repo, dynamodb):
    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.delete_buyer_request(1)

    dynamodb.delete_item.assert_called_once()


@pytest.mark.asyncio
async def test_delete_buyer_request_client_error(repo, dynamodb):
    dynamodb.delete_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}}, "op"
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.delete_buyer_request(1)
