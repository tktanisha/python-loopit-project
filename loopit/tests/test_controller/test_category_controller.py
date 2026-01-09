import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.category_controller import (
    create_category,
    get_all_category,
    update_category,
    delete_category,
)
from schemas.category import CategoryRequest
from models.category import Category


@pytest.mark.asyncio
async def test_create_category_success():
    service = MagicMock()
    service.create_category = AsyncMock(return_value=None)

    payload = CategoryRequest(
        name="Electronics",
        price=100.0,
        security=20.0,
    )

    resp = await create_category(payload, service)

    service.create_category.assert_awaited_once()
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_category_failure():
    service = MagicMock()
    service.create_category = AsyncMock(side_effect=Exception("db error"))

    payload = CategoryRequest(
        name="Electronics",
        price=100.0,
        security=20.0,
    )

    resp = await create_category(payload, service)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_all_category_success():
    service = MagicMock()
    service.get_all_categories = AsyncMock(
        return_value=[
            Category(id=1, name="Cat1", price=10, security=1),
            Category(id=2, name="Cat2", price=20, security=2),
        ]
    )

    resp = await get_all_category(service)

    service.get_all_categories.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_category_failure():
    service = MagicMock()
    service.get_all_categories = AsyncMock(side_effect=Exception("something broke"))

    resp = await get_all_category(service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_update_category_success():
    service = MagicMock()
    service.update_category = AsyncMock(return_value=None)

    payload = CategoryRequest(
        name="Updated",
        price=200.0,
        security=30.0,
    )

    resp = await update_category(1, payload, service)

    service.update_category.assert_awaited_once()
    assert resp.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.asyncio
async def test_update_category_failure():
    service = MagicMock()
    service.update_category = AsyncMock(side_effect=Exception("update failed"))

    payload = CategoryRequest(
        name="Updated",
        price=200.0,
        security=30.0,
    )

    resp = await update_category(1, payload, service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_category_success():
    service = MagicMock()
    service.delete_category = AsyncMock(return_value=None)

    resp = await delete_category(1, service)

    service.delete_category.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_category_failure():
    service = MagicMock()
    service.delete_category = AsyncMock(side_effect=Exception("delete error"))

    resp = await delete_category(1, service)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
