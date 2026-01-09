import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions
from datetime import datetime, timezone

from repository.return_request_repository import ReturnRequestRepo
from models.return_request import ReturnRequest
from models.enums.return_req_status import ReturnStatus


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr(
        "repository.return_request_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return ReturnRequestRepo(dynamodb=dynamodb)


@pytest.mark.asyncio
async def test_create_return_request_success(repo, dynamodb):
    rr = MagicMock(spec=ReturnRequest)
    rr.id = None
    rr.order_id = 10
    rr.requested_by = 5
    rr.status = ReturnStatus.Pending

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create_return_request(rr)

    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_create_return_request_client_error(repo, dynamodb):
    rr = MagicMock(spec=ReturnRequest)
    rr.id = 1
    rr.order_id = 10
    rr.requested_by = 5
    rr.status = ReturnStatus.Pending

    dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "PutItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create_return_request(rr)


@pytest.mark.asyncio
async def test_update_return_request_status_success(repo, dynamodb):
    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.update_return_request_status(1, ReturnStatus.Approved.value)

    dynamodb.update_item.assert_called_once()


@pytest.mark.asyncio
async def test_update_return_request_status_client_error(repo, dynamodb):
    dynamodb.update_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "UpdateItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.update_return_request_status(1, ReturnStatus.Rejected.value)


@pytest.mark.asyncio
async def test_get_all_return_requests_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "OrderID": {"N": "10"},
                "RequestedBy": {"N": "5"},
                "Status": {"S": ReturnStatus.Pending.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            },
            {
                "ID": {"N": "2"},
                "OrderID": {"N": "11"},
                "RequestedBy": {"N": "6"},
                "Status": {"S": ReturnStatus.Approved.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            },
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        res = await repo.get_all_return_requests(
            [ReturnStatus.Pending.value]
        )

    assert len(res) == 1
    assert res[0].id == 1


@pytest.mark.asyncio
async def test_get_all_return_requests_no_filter(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "OrderID": {"N": "10"},
                "RequestedBy": {"N": "5"},
                "Status": {"S": ReturnStatus.Pending.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        res = await repo.get_all_return_requests(None)

    assert len(res) == 1


@pytest.mark.asyncio
async def test_get_all_return_requests_client_error(repo, dynamodb):
    dynamodb.query.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "Query",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.get_all_return_requests(None)


@pytest.mark.asyncio
async def test_get_return_request_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "OrderID": {"N": "10"},
            "RequestedBy": {"N": "5"},
            "Status": {"S": ReturnStatus.Pending.value},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        rr = await repo.get_return_request_by_id(1)

    assert rr is not None
    assert rr.id == 1
    assert rr.order_id == 10


@pytest.mark.asyncio
async def test_get_return_request_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        rr = await repo.get_return_request_by_id(1)

    assert rr is None


@pytest.mark.asyncio
async def test_get_return_request_by_id_client_error(repo, dynamodb):
    dynamodb.get_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "GetItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.get_return_request_by_id(1)


@pytest.mark.asyncio
async def test_save_no_op(repo):
    await repo.save()
