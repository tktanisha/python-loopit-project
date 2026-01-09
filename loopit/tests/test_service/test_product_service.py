import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from service.product_service import ProductService
from models.enums.user import Role
from models.product import Product, ProductFilter
from schemas.product import ProductRequest


@pytest.fixture
def product_repo():
    return AsyncMock()


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def service(product_repo, user_repo):
    return ProductService(product_repo=product_repo, user_repo=user_repo)


@pytest.mark.asyncio
async def test_get_all_products_success(service, product_repo):
    product_repo.find_all.return_value = ["p1", "p2"]
    result = await service.get_all_products(
        search="test",
        lender_id="1",
        category_id="2",
        is_available="true",
    )
    assert result == ["p1", "p2"]
    product_repo.find_all.assert_called_once()
    filters = product_repo.find_all.call_args[0][0]
    assert isinstance(filters, ProductFilter)


@pytest.mark.asyncio
async def test_get_product_by_id_success(service, product_repo):
    product_repo.find_by_id.return_value = "product"
    result = await service.get_product_by_id(1)
    assert result == "product"


@pytest.mark.asyncio
async def test_get_product_by_id_invalid_id(service):
    with pytest.raises(RuntimeError):
        await service.get_product_by_id(0)


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(service, product_repo):
    product_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.get_product_by_id(1)


@pytest.mark.asyncio
async def test_create_product_success(service, product_repo, monkeypatch):
    mock_product = MagicMock()

    monkeypatch.setattr(
        "service.product_service.Product",
        lambda **kwargs: mock_product
    )

    product_req = MagicMock(
        category_id=1,
        name="name",
        description="desc",
        duration=5,
        image_url="url",
    )

    user_ctx = MagicMock(role="lender", user_id=10)

    await service.create_product(product_req, user_ctx)

    product_repo.create.assert_called_once_with(mock_product)



@pytest.mark.asyncio
async def test_create_product_unauthenticated(service):
    with pytest.raises(RuntimeError):
        await service.create_product(MagicMock(), None)


@pytest.mark.asyncio
async def test_create_product_not_lender(service):
    user_ctx = MagicMock(role="buyer", user_id=1)
    with pytest.raises(RuntimeError):
        await service.create_product(MagicMock(), user_ctx)


@pytest.mark.asyncio
async def test_update_product_success(service, product_repo):
    product = MagicMock(lender_id=5)
    product_resp = MagicMock(product=product)
    product_repo.find_by_id.return_value = product_resp
    user_ctx = {"role": "lender", "user_id": 5}

    await service.update_product(
        id=1,
        name="n",
        description="d",
        category_id=2,
        duration=3,
        is_available=False,
        image_url=None,
        user_ctx=user_ctx,
    )

    assert product.name == "n"
    assert product.description == "d"
    assert product.category_id == 2
    assert product.duration == 3
    assert product.is_available is False
    product_repo.update.assert_called_once_with(product)


@pytest.mark.asyncio
async def test_update_product_not_owner(service, product_repo):
    product = MagicMock(lender_id=99)
    product_repo.find_by_id.return_value = MagicMock(product=product)
    user_ctx = {"role": "lender", "user_id": 5}
    with pytest.raises(RuntimeError):
        await service.update_product(1, "n", "d", 1, 1, True, None, user_ctx)


@pytest.mark.asyncio
async def test_delete_product_success(service, product_repo):
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=5)
    )
    user_ctx = {"role": "lender", "user_id": 5}
    await service.delete_product(1, user_ctx)
    product_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_product_not_found(service, product_repo):
    product_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.delete_product(1, {"user_id": 1})


@pytest.mark.asyncio
async def test_delete_product_not_owner(service, product_repo):
    product_repo.find_by_id.return_value = MagicMock(
        product=MagicMock(lender_id=99)
    )
    with pytest.raises(RuntimeError):
        await service.delete_product(1, {"user_id": 5})
