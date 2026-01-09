import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.society_controller import (
    create_society,
    get_all_societies,
    update_society,
    delete_society,
)
from schemas.society import SocietyRequest


@pytest.mark.asyncio
async def test_create_society_success():
    service = MagicMock()
    service.create_society = AsyncMock(return_value=None)

    society = SocietyRequest(
        name="My Society",
        location="City",
        pincode="123456",
    )

    resp = await create_society(society, service)

    service.create_society.assert_awaited_once()
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_society_failure():
    service = MagicMock()
    service.create_society = AsyncMock(side_effect=Exception("error"))

    society = SocietyRequest(
        name="My Society",
        location="City",
        pincode="123456",
    )

    resp = await create_society(society, service)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_all_societies_success():
    service = MagicMock()
    service.get_all_societies = AsyncMock(return_value=[])

    resp = await get_all_societies(service)

    service.get_all_societies.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_societies_failure():
    service = MagicMock()
    service.get_all_societies = AsyncMock(side_effect=Exception("db error"))

    resp = await get_all_societies(service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_update_society_success():
    service = MagicMock()
    service.update_society = AsyncMock(return_value=None)

    society = SocietyRequest(
        name="Updated",
        location="New City",
        pincode="654321",
    )

    resp = await update_society(
        id=1,
        society=society,
        society_service=service,
    )

    service.update_society.assert_awaited_once()
    assert resp.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.asyncio
async def test_update_society_failure():
    service = MagicMock()
    service.update_society = AsyncMock(side_effect=Exception("fail"))

    society = SocietyRequest(
        name="Updated",
        location="New City",
        pincode="654321",
    )

    resp = await update_society(
        id=1,
        society=society,
        society_service=service,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_society_success():
    service = MagicMock()
    service.delete_society = AsyncMock(return_value=None)

    resp = await delete_society(1, service)

    service.delete_society.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_society_failure():
    service = MagicMock()
    service.delete_society = AsyncMock(side_effect=Exception("error"))

    resp = await delete_society(1, service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
