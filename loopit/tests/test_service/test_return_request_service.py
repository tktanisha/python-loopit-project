import pytest
from unittest.mock import AsyncMock, MagicMock

from service.return_request_service import ReturnRequestService
from models.enums.order_status import OrderStatus
from models.enums.return_req_status import ReturnStatus
from models.return_request import ReturnRequest


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
    return ReturnRequestService(
        order_repo=order_repo,
        product_repo=product_repo,
        return_request_repo=return_request_repo,
    )


@pytest.mark.asyncio
async def test_create_return_request_success(service, order_repo, product_repo, return_request_repo):
    order_repo.get_order_by_id.return_value = MagicMock(
        product_id=10,
        status=OrderStatus.InUse,
    )
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=5)
    )

    await service.create_return_request(user_id=5, order_id=1)

    order_repo.update_order_status.assert_called_once_with(1, OrderStatus.ReturnRequested.value)
    return_request_repo.create_return_request.assert_called_once()
    rr = return_request_repo.create_return_request.call_args[0][0]
    assert isinstance(rr, ReturnRequest)
    assert rr.order_id == 1
    assert rr.requested_by == 5
    assert rr.status == ReturnStatus.Pending


@pytest.mark.asyncio
async def test_create_return_request_order_not_found(service, order_repo):
    order_repo.get_order_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.create_return_request(1, 1)


@pytest.mark.asyncio
async def test_create_return_request_invalid_order_status(service, order_repo):
    order_repo.get_order_by_id.return_value = MagicMock(
        status=OrderStatus.Returned
    )

    with pytest.raises(RuntimeError):
        await service.create_return_request(user_id=1, order_id=1)


@pytest.mark.asyncio
async def test_create_return_request_product_not_found(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(
        product_id=10,
        status=OrderStatus.InUse,
    )
    product_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.create_return_request(1, 1)


@pytest.mark.asyncio
async def test_create_return_request_not_lender(service, order_repo, product_repo):
    order_repo.get_order_by_id.return_value = MagicMock(
        product_id=10,
        status=OrderStatus.InUse,
    )
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=99)
    )
    with pytest.raises(RuntimeError):
        await service.create_return_request(1, 1)


@pytest.mark.asyncio
async def test_update_return_request_status_success(service, order_repo, return_request_repo):
    return_request_repo.get_return_request_by_id.return_value = MagicMock(
        id=1,
        order_id=10,
        status=ReturnStatus.Pending,
    )
    order_repo.get_order_by_id.return_value = MagicMock(
        user_id=5
    )

    await service.update_return_request_status(
        user_id=5,
        req_id=1,
        new_status=ReturnStatus.Approved,
    )

    return_request_repo.update_return_request_status.assert_called_once_with(
        1, ReturnStatus.Approved.value
    )


@pytest.mark.asyncio
async def test_update_return_request_status_invalid_status(service):
    with pytest.raises(RuntimeError):
        await service.update_return_request_status(1, 1, ReturnStatus.Pending)


@pytest.mark.asyncio
async def test_update_return_request_status_not_found(service, return_request_repo):
    return_request_repo.get_return_request_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.update_return_request_status(1, 1, ReturnStatus.Approved)


@pytest.mark.asyncio
async def test_update_return_request_status_not_owner(service, order_repo, return_request_repo):
    return_request_repo.get_return_request_by_id.return_value = MagicMock(
        order_id=10,
        status=ReturnStatus.Pending,
    )
    order_repo.get_order_by_id.return_value = MagicMock(
        user_id=99
    )
    with pytest.raises(RuntimeError):
        await service.update_return_request_status(1, 1, ReturnStatus.Approved)


@pytest.mark.asyncio
async def test_get_pending_return_requests_success(service, order_repo, return_request_repo):
    req1 = MagicMock(order_id=1)
    req2 = MagicMock(order_id=2)

    return_request_repo.get_all_return_requests.return_value = [req1, req2]

    order_repo.get_order_by_id.side_effect = [
        MagicMock(user_id=5),
        MagicMock(user_id=99),
    ]

    result = await service.get_pending_return_requests(user_id=5)

    assert result == [req1]
    return_request_repo.get_all_return_requests.assert_called_once_with(
        [ReturnStatus.Pending.value]
    )
