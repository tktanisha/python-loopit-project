import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions

from repository.category_repository import CategoryRepo
from models.category import Category


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr(
        "repository.category_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return CategoryRepo(dynamodb=dynamodb)


@pytest.mark.asyncio
async def test_create_category_success(repo, dynamodb):
    category = MagicMock(spec=Category)
    category.id = None
    category.model_dump.return_value = {
        "ID": None,
        "Name": "Electronics",
        "Price": 100,
        "Security": 20,
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create_category(category)

    assert category.id is not None
    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_create_category_exception(repo, dynamodb):
    category = MagicMock(spec=Category)
    category.model_dump.return_value = {}

    dynamodb.put_item.side_effect = Exception("db error")

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create_category(category)


@pytest.mark.asyncio
async def test_get_all_categories_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "Name": {"S": "Electronics"},
                "Price": {"N": "100"},
                "Security": {"N": "20"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        result = await repo.get_all_categories()

    assert len(result) == 1
    assert isinstance(result[0], Category)
    assert result[0].id == 1


@pytest.mark.asyncio
async def test_get_all_categories_client_error(repo, dynamodb):
    dynamodb.query.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "Query",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.get_all_categories()


@pytest.mark.asyncio
async def test_find_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "Name": {"S": "Electronics"},
            "Price": {"N": "100"},
            "Security": {"N": "20"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        category = await repo.find_by_id(1)

    assert category is not None
    assert category.id == 1


@pytest.mark.asyncio
async def test_find_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        category = await repo.find_by_id(1)

    assert category is None


@pytest.mark.asyncio
async def test_update_category_success(repo, dynamodb):
    category = MagicMock(spec=Category)
    category.id = 1
    category.model_dump.return_value = {
        "ID": 1,
        "Name": "Updated",
        "Price": 200,
        "Security": 50,
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.update_category(category)

    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_update_category_missing_id(repo):
    category = MagicMock(spec=Category)
    category.id = None

    with pytest.raises(RuntimeError):
        await repo.update_category(category)


@pytest.mark.asyncio
async def test_update_category_client_error(repo, dynamodb):
    category = MagicMock(spec=Category)
    category.id = 1
    category.model_dump.return_value = {}

    dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}},
        "PutItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.update_category(category)


@pytest.mark.asyncio
async def test_delete_category_success(repo, dynamodb):
    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.delete_category(1)

    dynamodb.delete_item.assert_called_once()


@pytest.mark.asyncio
async def test_delete_category_client_error(repo, dynamodb):
    dynamodb.delete_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}},
        "DeleteItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.delete_category(1)
