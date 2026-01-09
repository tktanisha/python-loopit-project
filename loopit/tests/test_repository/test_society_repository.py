import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions

from repository.society_repository import SocietyRepo
from models.society import Society


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr(
        "repository.society_repository.settings.DDB_TABLE_NAME",
        "test-table",
    )
    return SocietyRepo(dynamodb=dynamodb)


@pytest.mark.asyncio
async def test_create_society_success(repo, dynamodb):
    society = MagicMock(spec=Society)
    society.id = None
    society.model_dump.return_value = {
        "ID": None,
        "Name": "Green Valley",
        "Location": "City",
        "Pincode": "123456",
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.create(society)

    assert society.id is not None
    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_create_society_client_error(repo, dynamodb):
    society = MagicMock(spec=Society)
    society.model_dump.return_value = {}

    dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "PutItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.create(society)


@pytest.mark.asyncio
async def test_find_all_societies_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "Name": {"S": "Green Valley"},
                "Location": {"S": "City"},
                "Pincode": {"S": "123456"},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        societies = await repo.find_all()

    assert len(societies) == 1
    assert isinstance(societies[0], Society)
    assert societies[0].id == 1


@pytest.mark.asyncio
async def test_find_all_societies_client_error(repo, dynamodb):
    dynamodb.query.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "500", "Message": "err"}},
        "Query",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.find_all()


@pytest.mark.asyncio
async def test_find_society_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "Name": {"S": "Green Valley"},
            "Location": {"S": "City"},
            "Pincode": {"S": "123456"},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        society = await repo.find_by_id(1)

    assert society is not None
    assert society.id == 1
    assert society.name == "Green Valley"


@pytest.mark.asyncio
async def test_find_society_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        society = await repo.find_by_id(1)

    assert society is None


@pytest.mark.asyncio
async def test_update_society_success(repo, dynamodb):
    society = MagicMock(spec=Society)
    society.id = 1
    society.model_dump.return_value = {
        "ID": 1,
        "Name": "Updated",
        "Location": "New City",
        "Pincode": "654321",
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.update(society)

    dynamodb.put_item.assert_called_once()


@pytest.mark.asyncio
async def test_update_society_missing_id(repo):
    society = MagicMock(spec=Society)
    society.id = None

    with pytest.raises(RuntimeError):
        await repo.update(society)


@pytest.mark.asyncio
async def test_update_society_client_error(repo, dynamodb):
    society = MagicMock(spec=Society)
    society.id = 1
    society.model_dump.return_value = {}

    dynamodb.put_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}},
        "PutItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.update(society)


@pytest.mark.asyncio
async def test_delete_society_success(repo, dynamodb):
    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.delete(1)

    dynamodb.delete_item.assert_called_once()


@pytest.mark.asyncio
async def test_delete_society_client_error(repo, dynamodb):
    dynamodb.delete_item.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}},
        "DeleteItem",
    )

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.delete(1)
