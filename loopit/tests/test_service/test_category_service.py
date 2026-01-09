import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from service.category_service import CategoryService
from models.category import Category


@pytest.fixture
def category_repo():
    return AsyncMock()


@pytest.fixture
def service(category_repo):
    return CategoryService(category_repo=category_repo)


@pytest.mark.asyncio
async def test_create_category_success(service, category_repo):
    category = MagicMock(spec=Category)
    await service.create_category(category)
    category_repo.create_category.assert_called_once_with(category=category)


@pytest.mark.asyncio
async def test_create_category_repo_exception(service, category_repo):
    category = MagicMock(spec=Category)
    category_repo.create_category.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.create_category(category)


@pytest.mark.asyncio
async def test_get_all_categories_success(service, category_repo):
    category_repo.get_all_categories.return_value = ["c1", "c2"]
    result = await service.get_all_categories()
    assert result == ["c1", "c2"]
    category_repo.get_all_categories.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_categories_exception(service, category_repo):
    category_repo.get_all_categories.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.get_all_categories()


@pytest.mark.asyncio
async def test_update_category_not_found(service, category_repo):
    category_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.update_category(1, "New", 10.5, 2.5)


@pytest.mark.asyncio
async def test_update_category_success(service, category_repo):
    category = MagicMock(spec=Category)
    category_repo.find_by_id.return_value = category
    await service.update_category(1, "Electronics", 100.5, 20.25)
    assert category.name == "Electronics"
    assert category.price == Decimal("100.5")
    assert category.security == Decimal("20.25")
    category_repo.update_category.assert_called_once_with(category)


@pytest.mark.asyncio
async def test_update_category_update_exception(service, category_repo):
    category = MagicMock(spec=Category)
    category_repo.find_by_id.return_value = category
    category_repo.update_category.side_effect = Exception("update failed")
    with pytest.raises(Exception):
        await service.update_category(1, "Electronics", 100, 10)


@pytest.mark.asyncio
async def test_delete_category_not_found(service, category_repo):
    category_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.delete_category(1)


@pytest.mark.asyncio
async def test_delete_category_success(service, category_repo):
    category_repo.find_by_id.return_value = MagicMock(spec=Category)
    await service.delete_category(1)
    category_repo.delete_category.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_category_exception(service, category_repo):
    category_repo.find_by_id.return_value = MagicMock(spec=Category)
    category_repo.delete_category.side_effect = Exception("delete failed")
    with pytest.raises(Exception):
        await service.delete_category(1)
