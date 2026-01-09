import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import botocore.exceptions
from datetime import datetime

from repository.product_repository import ProductRepo
from models.product import Product, ProductFilter, ProductResponse
from models.category import Category
from models.user import User


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def category_repo():
    return MagicMock()


@pytest.fixture
def user_repo():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, category_repo, user_repo, monkeypatch):
    monkeypatch.setattr(
        "repository.product_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return ProductRepo(
        dynamodb=dynamodb,
        category_repo=category_repo,
        user_repo=user_repo,
    )


@pytest.mark.asyncio
async def test_create_product_success(repo, dynamodb):
    product = MagicMock(spec=Product)
    product.id = None
    product.lender_id = 1
    product.category_id = 2
    product.name = "Phone"
    product.description = "Nice"
    product.duration = 10
    product.is_available = True
    product.image_url = None
    product.created_at = datetime.now()

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        await repo.create(product)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_client_error(repo, dynamodb):
    product = MagicMock(spec=Product)
    product.id = None
    product.lender_id = 1
    product.category_id = 2
    product.name = "Phone"
    product.description = "Nice"
    product.duration = 10
    product.is_available = True
    product.image_url = None
    product.created_at = datetime.now()

    dynamodb.transact_write_items.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "TransactWriteItems",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        with pytest.raises(RuntimeError):
            await repo.create(product)


@pytest.mark.asyncio
async def test_find_by_id_success(repo, dynamodb, category_repo, user_repo):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "LenderID": {"N": "10"},
            "CategoryID": {"N": "20"},
            "Name": {"S": "Phone"},
            "Description": {"S": "Nice"},
            "Duration": {"N": "10"},
            "IsAvailable": {"BOOL": True},
            "CreatedAt": {"S": "2024-01-01T00:00:00"},
            "ImageUrl": {"S": ""},
        }
    }

    category_repo.find_by_id.return_value = MagicMock(spec=Category)
    user_repo.find_by_id.return_value = MagicMock(spec=User)

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        resp = await repo.find_by_id(1)

    assert isinstance(resp, ProductResponse)
    assert resp.product.id == 1


@pytest.mark.asyncio
async def test_find_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        resp = await repo.find_by_id(1)

    assert resp is None


@pytest.mark.asyncio
async def test_find_all_products_success(repo, dynamodb, category_repo, user_repo):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "LenderID": {"N": "10"},
                "CategoryID": {"N": "20"},
                "Name": {"S": "Phone"},
                "Description": {"S": "Nice"},
                "Duration": {"N": "10"},
                "IsAvailable": {"BOOL": True},
                "CreatedAt": {"S": "2024-01-01T00:00:00"},
                "ImageUrl": {"S": ""},
            }
        ]
    }

    category_repo.find_by_id = AsyncMock(return_value=MagicMock(spec=Category))
    user_repo.find_by_id = AsyncMock(return_value=MagicMock(spec=User))

    filters = ProductFilter(
        search=None,
        lender_id=None,
        category_id=None,
        is_available=None,
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        results = await repo.find_all(filters)

    assert len(results) == 1
    assert isinstance(results[0], ProductResponse)


@pytest.mark.asyncio
async def test_update_product_success(repo, dynamodb):
    existing_product = MagicMock()
    existing_product.product.category_id = 1
    existing_product.product.name = "Old"

    repo.find_by_id = AsyncMock(return_value=existing_product)

    product = MagicMock(spec=Product)
    product.id = 1
    product.lender_id = 10
    product.category_id = 2
    product.name = "New"
    product.description = "Desc"
    product.duration = 5
    product.is_available = True

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        await repo.update(product)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_update_product_not_found(repo):
    repo.find_by_id = AsyncMock(return_value=None)

    product = MagicMock(spec=Product)
    product.id = 1

    with pytest.raises(RuntimeError):
        await repo.update(product)


@pytest.mark.asyncio
async def test_delete_product_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "Name": {"S": "Phone"},
            "LenderID": {"N": "10"},
            "CategoryID": {"N": "20"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        await repo.delete(1)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_delete_product_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        with pytest.raises(RuntimeError):
            await repo.delete(1)


@pytest.mark.asyncio
async def test_create_product_unexpected_error(repo, dynamodb):
    product = MagicMock(spec=Product)
    product.id = None
    product.lender_id = 1
    product.category_id = 2
    product.name = "Phone"
    product.description = "Nice"
    product.duration = 10
    product.is_available = True
    product.image_url = None
    product.created_at = datetime.now()

    dynamodb.transact_write_items.side_effect = Exception("boom")

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)
):
        with pytest.raises(RuntimeError):
            await repo.create(product)
