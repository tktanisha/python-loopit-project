import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import botocore.exceptions
from datetime import datetime, timezone
from decimal import Decimal

from repository.order_repository import OrderRepo
from models.orders import Order
from models.enums.order_status import OrderStatus


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def product_repo():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, product_repo, monkeypatch):
    monkeypatch.setattr(
        "repository.order_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return OrderRepo(dynamodb=dynamodb, product_repo=product_repo)


@pytest.mark.asyncio
async def test_create_order_success(repo, dynamodb, product_repo):
    order = MagicMock(spec=Order)
    order.id = None
    order.product_id = 10
    order.user_id = 5
    order.start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    order.end_date = datetime(2024, 1, 2, tzinfo=timezone.utc)
    order.total_amount = 100.5
    order.security_amount = 20.0
    order.status = OrderStatus.InUse

    product_repo.find_by_id = AsyncMock(
        product=MagicMock(lender_id=99)
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create_order(order)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_create_order_product_not_found(repo, product_repo):
    order = MagicMock(spec=Order)
    order.id = None
    order.product_id = 1
    order.user_id = 1
    order.start_date = datetime.now(timezone.utc)
    order.end_date = datetime.now(timezone.utc)
    order.total_amount = 10
    order.security_amount = 1
    order.status = OrderStatus.InUse

    product_repo.find_by_id.return_value = None

    with pytest.raises(RuntimeError):
        await repo.create_order(order)


@pytest.mark.asyncio
async def test_create_order_client_error(repo, dynamodb, product_repo):
    order = MagicMock(spec=Order)
    order.id = 1
    order.product_id = 10
    order.user_id = 5
    order.start_date = datetime.now(timezone.utc)
    order.end_date = datetime.now(timezone.utc)
    order.total_amount = 100
    order.security_amount = 20
    order.status = OrderStatus.InUse

    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=1)
    )

    dynamodb.transact_write_items.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "TransactWriteItems",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create_order(order)


@pytest.mark.asyncio
async def test_update_order_status_success(repo, dynamodb, product_repo):
    repo.get_order_by_id = AsyncMock(
        return_value=MagicMock(
            product_id=10,
            user_id=5,
        )
    )
    product_repo.find_by_id = AsyncMock(
        return_value=MagicMock(
            product=MagicMock(lender_id=99)
        )
    )
    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.update_order_status(1, OrderStatus.Returned.value)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_update_order_status_not_found(repo):
    repo.get_order_by_id = MagicMock(return_value=None)

    with pytest.raises(RuntimeError):
        await repo.update_order_status(1, OrderStatus.Returned.value)


@pytest.mark.asyncio
async def test_get_order_history_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "ProductID": {"N": "10"},
                "UserID": {"N": "5"},
                "StartDate": {"S": "2024-01-01T00:00:00Z"},
                "EndDate": {"S": "2024-01-02T00:00:00Z"},
                "TotalAmount": {"N": "100"},
                "SecurityAmount": {"N": "20"},
                "Status": {"S": OrderStatus.InUse.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        orders = await repo.get_order_history(
            user_id=5,
            filter_statuses=[OrderStatus.InUse.value],
        )

    assert len(orders) == 1
    assert orders[0].id == 1


@pytest.mark.asyncio
async def test_get_lender_orders_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "ProductID": {"N": "10"},
                "UserID": {"N": "5"},
                "StartDate": {"S": "2024-01-01T00:00:00Z"},
                "EndDate": {"S": "2024-01-02T00:00:00Z"},
                "TotalAmount": {"N": "100"},
                "SecurityAmount": {"N": "20"},
                "Status": {"S": OrderStatus.InUse.value},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        orders = await repo.get_lender_orders(99)

    assert len(orders) == 1
    assert orders[0].id == 1


@pytest.mark.asyncio
async def test_get_order_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "ProductID": {"N": "10"},
            "UserID": {"N": "5"},
            "StartDate": {"S": "2024-01-01T00:00:00Z"},
            "EndDate": {"S": "2024-01-02T00:00:00Z"},
            "TotalAmount": {"N": "100"},
            "SecurityAmount": {"N": "20"},
            "Status": {"S": OrderStatus.InUse.value},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        order = await repo.get_order_by_id(1)

    assert order is not None
    assert order.id == 1


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        order = await repo.get_order_by_id(1)

    assert order is None
