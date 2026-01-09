import pytest
from unittest.mock import MagicMock, AsyncMock

from fastapi import status

from controller.buy_request_controller import (
    create_buyer_request,
    update_buyer_request_status,
    get_all_buyer_requests,
)
from models.enums.buy_request import BuyRequestStatus


@pytest.mark.asyncio
async def test_create_buyer_request_success():
    service = MagicMock()
    service.create_buyer_request = AsyncMock(return_value=None)

    user_ctx = {"user_id": 1}

    resp = await create_buyer_request(
        product_id=10,
        buyer_request_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_201_CREATED
    service.create_buyer_request.assert_called_once_with(10, user_ctx)


@pytest.mark.asyncio
async def test_create_buyer_request_failure():
    service = MagicMock()
    service.create_buyer_request = AsyncMock(side_effect=Exception("error"))

    user_ctx = {"user_id": 1}

    resp = await create_buyer_request(
        product_id=10,
        buyer_request_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.body.decode()
    assert "failed to create buyer request" in body


@pytest.mark.asyncio
async def test_update_buyer_request_status_success():
    service = MagicMock()
    service.update_buyer_request_status = AsyncMock(return_value=None)

    user_ctx = {"user_id": 1}

    resp = await update_buyer_request_status(
        request_id=5,
        status_str=BuyRequestStatus.Pending.value,
        buyer_request_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_200_OK
    service.update_buyer_request_status.assert_called_once()


@pytest.mark.asyncio
async def test_update_buyer_request_status_invalid_status():
    service = MagicMock()

    user_ctx = {"user_id": 1}

    resp = await update_buyer_request_status(
        request_id=5,
        status_str="not-a-real-status",
        buyer_request_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.body.decode()
    assert "invalid status value" in body


@pytest.mark.asyncio
async def test_update_buyer_request_status_service_error():
    service = MagicMock()
    service.update_buyer_request_status = AsyncMock(side_effect=Exception("db error"))

    user_ctx = {"user_id": 1}

    resp = await update_buyer_request_status(
        request_id=5,
        status_str=BuyRequestStatus.Pending.value,
        buyer_request_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.body.decode()
    assert "failed to update status" in body


@pytest.mark.asyncio
async def test_get_all_buyer_requests_success():
    buyer_service = MagicMock()
    product_service = MagicMock()

    mock_req = MagicMock()
    mock_req.product_id = 10
    mock_req.model_dump.return_value = {"id": 1}

    buyer_service.get_all_buyer_requests = AsyncMock(return_value=[mock_req])

    mock_product = MagicMock()
    mock_product.model_dump.return_value = {"id": 10}

    product_service.get_product_by_id = AsyncMock(return_value=mock_product)

    resp = await get_all_buyer_requests(
        product_id=None,
        status_str=None,
        buyer_request_service=buyer_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_200_OK
    body = resp.body.decode()
    assert "buyer request fetched successfully" in body


@pytest.mark.asyncio
async def test_get_all_buyer_requests_service_error():
    buyer_service = MagicMock()
    product_service = MagicMock()

    buyer_service.get_all_buyer_requests = AsyncMock(side_effect=Exception("query failed"))

    resp = await get_all_buyer_requests(
        product_id=None,
        status_str=None,
        buyer_request_service=buyer_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    body = resp.body.decode()
    assert "failed to fetch buyer requests" in body


@pytest.mark.asyncio
async def test_get_all_buyer_requests_product_fetch_error():
    buyer_service = MagicMock()
    product_service = MagicMock()

    mock_req = MagicMock()
    mock_req.product_id = 99
    mock_req.model_dump.return_value = {"id": 1}

    buyer_service.get_all_buyer_requests = AsyncMock(return_value=[mock_req])
    product_service.get_product_by_id = AsyncMock(side_effect=Exception("product error"))

    resp = await get_all_buyer_requests(
        product_id=None,
        status_str=None,
        buyer_request_service=buyer_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
