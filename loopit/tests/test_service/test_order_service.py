import pytest
from unittest.mock import AsyncMock, MagicMock

from service.order_service import OrderService
from models.enums.order_status import OrderStatus
from models.enums.user import Role
from models.orders import Order


@pytest.fixture
def order_repo():
    return AsyncMock()


@pytest.fixture
def product_repo():
    return AsyncMock()


@pytest.fixture
def return_request_repo():
    return AsyncMock()


@pytest.fixture
def service(order_repo, product_repo, return_request_repo):
    return OrderService(
        order_repo=order_repo,
        product_repo=product_repo,
        return_request_repo=return_request_repo,
    )


@pytest.mark.asyncio
async def test_update_order_status_success(service, order_repo):
    order_repo.get_order_by_id.return_value = MagicMock(status=OrderStatus.InUse)
    await service.update_order_status(1, OrderStatus.InUse)
    order_repo.update_order_status.assert_called_once_with(1, OrderStatus.InUse.value)


@pytest.mark.asyncio
async def test_update_order_status_not_found(service, order_repo):
    order_repo.get_order_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.update_order_status(1, OrderStatus.InUse)


@pytest.mark.asyncio
async def test_update_order_status_invalid_return_transition(service, order_repo):
    order_repo.get_order_by_id.return_value = MagicMock(status=OrderStatus.InUse)
    with pytest.raises(RuntimeError):
        await service.update_order_status(1, OrderStatus.Returned)


@pytest.mark.asyncio
async def test_get_order_history_success(service, order_repo):
    order_repo.get_order_history.return_value = ["o1", "o2"]
    user_ctx = {"user_id": 5}
    result = await service.get_order_history(user_ctx, [OrderStatus.InUse])
    assert result == ["o1", "o2"]
    order_repo.get_order_history.assert_called_once_with(5, [OrderStatus.InUse.value])


@pytest.mark.asyncio
async def test_get_lender_orders_success(service, order_repo):
    user_ctx = {"user_id": 10, "role": "lender"}
    order_repo.get_lender_orders.return_value = ["o1"]
    result = await service.get_lender_orders(user_ctx)
    assert result == ["o1"]
    order_repo.get_lender_orders.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_get_lender_orders_unauthorized(service):
    with pytest.raises(RuntimeError):
        await service.get_lender_orders({"user_id": 1, "role": "buyer"})


@pytest.mark.asyncio
async def test_get_lender_orders_invalid_lender(service):
    with pytest.raises(RuntimeError):
        await service.get_lender_orders({"user_id": 0, "role": "lender"})


@pytest.mark.asyncio
async def test_mark_order_as_returned_success(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=20)
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=5)
    )
    await service.mark_order_as_returned(1, {"user_id": 5})
    order_repo.update_order_status.assert_called_once_with(1, OrderStatus.Returned.value)


@pytest.mark.asyncio
async def test_mark_order_as_returned_order_not_found(service, order_repo):
    order_repo.get_order_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.mark_order_as_returned(1, {"user_id": 5})


@pytest.mark.asyncio
async def test_mark_order_as_returned_product_not_found(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=20)
    product_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.mark_order_as_returned(1, {"user_id": 5})


@pytest.mark.asyncio
async def test_mark_order_as_returned_unauthorized_lender(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(product_id=20)
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=99)
    )
    with pytest.raises(RuntimeError):
        await service.mark_order_as_returned(1, {"user_id": 5})
