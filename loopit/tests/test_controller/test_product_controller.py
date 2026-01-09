import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.product_controller import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)
from schemas.product import ProductRequest
from models.enums.user import Role


@pytest.mark.asyncio
async def test_get_all_products_success():
    product_service = MagicMock()
    product_service.get_all_products = AsyncMock(return_value=[{"id": 1}])

    resp = await get_all_products(
        search=None,
        lender_id=None,
        category_id=None,
        is_available=None,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_200_OK
    product_service.get_all_products.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_products_failure():
    product_service = MagicMock()
    product_service.get_all_products = AsyncMock(side_effect=Exception("db error"))

    resp = await get_all_products(
        search=None,
        lender_id=None,
        category_id=None,
        is_available=None,
        product_service=product_service,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_product_by_id_success():
    product_service = MagicMock()
    product_service.get_product_by_id = AsyncMock(return_value={"id": 1})

    resp = await get_product_by_id(1, product_service)

    assert resp.status_code == status.HTTP_200_OK
    product_service.get_product_by_id.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_product_by_id_not_found():
    product_service = MagicMock()
    product_service.get_product_by_id = AsyncMock(side_effect=Exception("not found"))

    resp = await get_product_by_id(99, product_service)

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_product_success():
    product_service = MagicMock()
    product_service.create_product = AsyncMock(return_value=None)

    product = ProductRequest(
        name="Phone",
        description="Nice",
        category_id=1,
        duration=5,
        is_available=True,
        image_url=None,
    )

    user_ctx = {"user_id": 1, "role": "lender"}

    resp = await create_product(product, product_service, user_ctx)

    assert resp.status_code == status.HTTP_201_CREATED
    product_service.create_product.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_product_forbidden():
    product_service = MagicMock()
    product = MagicMock()

    user_ctx = {"user_id": 1, "role": "buyer"}

    resp = await create_product(product, product_service, user_ctx)

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_product_success():
    product_service = MagicMock()
    product_service.update_product = AsyncMock(return_value=None)

    product = ProductRequest(
        name="Updated",
        description="Desc",
        category_id=1,
        duration=10,
        is_available=True,
        image_url=None,
    )

    user_ctx = {"user_id": 1, "role": Role.lender}

    resp = await update_product(
        id=1,
        product=product,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_200_OK
    product_service.update_product.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_product_forbidden():
    product_service = MagicMock()
    product = MagicMock()

    user_ctx = {"user_id": 1, "role": "buyer"}

    resp = await update_product(
        id=1,
        product=product,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_product_success():
    product_service = MagicMock()
    product_service.delete_product = AsyncMock(return_value=None)

    user_ctx = {"user_id": 1, "role": "lender"}

    resp = await delete_product(
        id=1,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_200_OK
    product_service.delete_product.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_product_forbidden():
    product_service = MagicMock()
    user_ctx = {"user_id": 1, "role": "buyer"}

    resp = await delete_product(
        id=1,
        product_service=product_service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN
