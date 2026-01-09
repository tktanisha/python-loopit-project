import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.order_controller import (
    get_order_history,
    mark_order_as_returned,
    get_lender_orders,
)
from models.enums.order_status import OrderStatus


@pytest.mark.asyncio
async def test_get_order_history_success():
    order_service = MagicMock()
    product_service = MagicMock()

    mock_order = MagicMock()
    mock_order.product_id = 10

    order_service.get_order_history = AsyncMock(return_value=[mock_order])
    product_service.get_product_by_id = AsyncMock(return_value=MagicMock())

    user_ctx = {"user_id": 1}

    resp = await get_order_history(
        user_ctx=user_ctx,
        status_str=None,
        order_service=order_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_200_OK
    order_service.get_order_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_order_history_invalid_status():
    order_service = MagicMock()
    product_service = MagicMock()
    user_ctx = {"user_id": 1}

    resp = await get_order_history(
        user_ctx=user_ctx,
        status_str="INVALID_STATUS",
        order_service=order_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_order_history_service_failure():
    order_service = MagicMock()
    product_service = MagicMock()

    order_service.get_order_history = AsyncMock(side_effect=Exception("db error"))

    user_ctx = {"user_id": 1}

    resp = await get_order_history(
        user_ctx=user_ctx,
        status_str=None,
        order_service=order_service,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_mark_order_as_returned_success():
    order_service = MagicMock()
    order_service.mark_order_as_returned = AsyncMock(return_value=None)

    user_ctx = {"user_id": 99}

    resp = await mark_order_as_returned(
        order_id=1,
        order_service=order_service,
        user_ctx=user_ctx,
    )

    order_service.mark_order_as_returned.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_mark_order_as_returned_failure():
    order_service = MagicMock()
    order_service.mark_order_as_returned = AsyncMock(side_effect=Exception("not allowed"))

    user_ctx = {"user_id": 99}

    resp = await mark_order_as_returned(
        order_id=1,
        order_service=order_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_lender_orders_success():
    order_service = MagicMock()
    product_service = MagicMock()

    mock_order = MagicMock()
    mock_order.product_id = 5

    order_service.get_lender_orders = AsyncMock(return_value=[mock_order])
    product_service.get_product_by_id = AsyncMock(return_value=MagicMock())

    user_ctx = {"user_id": 10, "role": "lender"}

    resp = await get_lender_orders(
        order_service=order_service,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_200_OK
    order_service.get_lender_orders.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_lender_orders_failure():
    order_service = MagicMock()
    product_service = MagicMock()

    order_service.get_lender_orders = AsyncMock(side_effect=Exception("error"))

    user_ctx = {"user_id": 10, "role": "lender"}

    resp = await get_lender_orders(
        order_service=order_service,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
