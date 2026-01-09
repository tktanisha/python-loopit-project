import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.return_request_controller import (
    get_pending_return_requests,
    create_return_request,
    update_return_request_status,
)


@pytest.mark.asyncio
async def test_get_pending_return_requests_success():
    service = MagicMock()
    service.get_pending_return_requests = AsyncMock(return_value=[])

    user_ctx = {"user_id": 1}

    resp = await get_pending_return_requests(user_ctx, service)

    service.get_pending_return_requests.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_pending_return_requests_failure():
    service = MagicMock()
    service.get_pending_return_requests = AsyncMock(side_effect=Exception("db error"))

    user_ctx = {"user_id": 1}

    resp = await get_pending_return_requests(user_ctx, service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_return_request_success():
    service = MagicMock()
    service.create_return_request = AsyncMock(return_value=None)

    user_ctx = {"user_id": 10}

    resp = await create_return_request(
        order_id=5,
        user_ctx=user_ctx,
        return_request_service=service,
    )

    service.create_return_request.assert_awaited_once()
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_return_request_failure():
    service = MagicMock()
    service.create_return_request = AsyncMock(side_effect=Exception("invalid order"))

    user_ctx = {"user_id": 10}

    resp = await create_return_request(
        order_id=5,
        user_ctx=user_ctx,
        return_request_service=service,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_update_return_request_status_invalid_status():
    service = MagicMock()
    user_ctx = {"user_id": 1}

    resp = await update_return_request_status(
        request_id=1,
        status_str="INVALID",
        user_ctx=user_ctx,
        return_request_service=service,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_update_return_request_status_success():
    service = MagicMock()
    service.update_return_request_status = AsyncMock(return_value=None)

    user_ctx = {"user_id": 1}

    resp = await update_return_request_status(
        request_id=1,
        status_str="Approved",
        user_ctx=user_ctx,
        return_request_service=service,
    )

    service.update_return_request_status.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_return_request_status_failure():
    service = MagicMock()
    service.update_return_request_status = AsyncMock(side_effect=Exception("not allowed"))

    user_ctx = {"user_id": 1}

    resp = await update_return_request_status(
        request_id=1,
        status_str="approved",
        user_ctx=user_ctx,
        return_request_service=service,
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
