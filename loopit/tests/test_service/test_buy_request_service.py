import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from service.buy_request_service import BuyRequestService
from models.buy_request import BuyingRequest
from models.orders import Order
from models.enums.buy_request import BuyRequestStatus
from models.enums.order_status import OrderStatus

@pytest.fixture
def product_repo():
    return AsyncMock()

@pytest.fixture
def buyer_request_repo():
    return AsyncMock()

@pytest.fixture
def category_repo():
    return AsyncMock()

@pytest.fixture
def order_repo():
    return AsyncMock()

@pytest.fixture
def service(product_repo, buyer_request_repo, category_repo, order_repo):
    return BuyRequestService(
        product_repo=product_repo,
        buyer_request_repo=buyer_request_repo,
        category_repo=category_repo,
        order_repo=order_repo,
    )

@pytest.mark.asyncio
async def test_create_buyer_request_success(service, product_repo, buyer_request_repo):
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(
            is_available=True,
            lender_id=2
        )
    )
    buyer_request_repo.get_all_buyer_requests.return_value = []

    user_ctx = {"user_id": 1}

    await service.create_buyer_request(product_id=10, user_ctx=user_ctx)

    buyer_request_repo.create_buyer_request.assert_called_once()
    created_req = buyer_request_repo.create_buyer_request.call_args[0][0]

    assert created_req.product_id == 10
    assert created_req.requested_by == 1
    assert created_req.status == BuyRequestStatus.Pending.value

@pytest.mark.asyncio
async def test_create_buyer_request_product_not_found(service, product_repo):
    product_repo.find_by_id.return_value = None

    with pytest.raises(RuntimeError):
        await service.create_buyer_request(1, {"user_id": 1})

@pytest.mark.asyncio
async def test_create_buyer_request_product_not_available(service, product_repo):
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(is_available=False)
    )

    with pytest.raises(RuntimeError):
        await service.create_buyer_request(1, {"user_id": 1})

@pytest.mark.asyncio
async def test_create_buyer_request_duplicate_pending(service, product_repo, buyer_request_repo):
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(is_available=True, lender_id=2)
    )

    buyer_request_repo.get_all_buyer_requests.return_value = [
        MagicMock(requested_by=1)
    ]

    with pytest.raises(RuntimeError):
        await service.create_buyer_request(1, {"user_id": 1})

@pytest.mark.asyncio
async def test_update_request_unauthorized(service):
    with pytest.raises(RuntimeError):
        await service.update_buyer_request_status(
            request_id=1,
            updated_status=BuyRequestStatus.Approved.value,
            user_ctx={"role": "buyer"},
        )

@pytest.mark.asyncio
async def test_update_request_invalid_status(service):
    with pytest.raises(RuntimeError):
        await service.update_buyer_request_status(
            request_id=1,
            updated_status="pending",
            user_ctx={"role": "lender"},
        )

@pytest.mark.asyncio
async def test_update_request_rejected(service, buyer_request_repo):
    buyer_request_repo.get_all_buyer_requests.return_value = [
        MagicMock(id=1)
    ]

    await service.update_buyer_request_status(
        request_id=1,
        updated_status=BuyRequestStatus.Rejected.value,
        user_ctx={"role": "lender"},
    )

    buyer_request_repo.update_status_buyer_request.assert_called_once_with(
        1, BuyRequestStatus.Rejected.value
    )

@pytest.mark.asyncio
async def test_update_request_approved(
    service, buyer_request_repo, product_repo, category_repo, order_repo
):
    buyer_request_repo.get_all_buyer_requests.return_value = [
        MagicMock(
            id=1,
            product_id=10,
            requested_by=5
        )
    ]

    product_repo.find_by_id.return_value = MagicMock(
        category=MagicMock(id=3)
    )

    category_repo.find_by_id.return_value = MagicMock(
        price=100.0,
        security=20.0
    )

    await service.update_buyer_request_status(
        request_id=1,
        updated_status=BuyRequestStatus.Approved.value,
        user_ctx={"role": "lender"},
    )

    order_repo.create_order.assert_called_once()
    buyer_request_repo.update_status_buyer_request.assert_called_once_with(
        1, BuyRequestStatus.Approved.value
    )

@pytest.mark.asyncio
async def test_get_all_buyer_requests(service, buyer_request_repo):
    buyer_request_repo.get_all_buyer_requests.return_value = ["req1", "req2"]

    result = await service.get_all_buyer_requests(1, ["pending"])

    assert result == ["req1", "req2"]
    buyer_request_repo.get_all_buyer_requests.assert_called_once()
