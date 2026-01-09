import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions
from datetime import datetime

from repository.user.user_repository import UserDynamoRepo
from models.user import User
from models.enums.user import Role
from exception.user import (
    UserNotFoundError,
    UserRepositoryError,
    UserAlreadyExistsError,
)


@pytest.fixture
def dynamodb():
    return MagicMock()


@pytest.fixture
def repo(dynamodb, monkeypatch):
    monkeypatch.setattr(
        "repository.user.user_repository.setting.DDB_TABLE_NAME",
        "test-table",
    )
    return UserDynamoRepo(dynamodb)


def test_find_by_email_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "FullName": {"S": "John Doe"},
            "Email": {"S": "a@b.com"},
            "PhoneNumber": {"S": "123"},
            "Address": {"S": "addr"},
            "PasswordHash": {"S": "hash"},
            "SocietyID": {"N": "10"},
            "Role": {"S": "user"},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    user = repo.find_by_email("a@b.com")

    assert isinstance(user, User)
    assert user.email == "a@b.com"
    assert user.id == 1


def test_find_by_email_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with pytest.raises(UserNotFoundError):
        repo.find_by_email("x@y.com")


def test_find_by_email_repo_error(repo, dynamodb):
    dynamodb.get_item.side_effect = Exception("ddb error")

    with pytest.raises(UserRepositoryError):
        repo.find_by_email("a@b.com")


def test_create_user_success(repo, dynamodb):
    user = User(
        id=None,
        full_name="John",
        email="a@b.com",
        phone_number="123",
        address="addr",
        password_hash="hash",
        society_id=1,
        role=Role.user,
        created_at=datetime.now(),
    )

    repo.create(user)

    assert user.id is not None
    dynamodb.transact_write_items.assert_called_once()


def test_create_user_already_exists(repo, dynamodb):
    dynamodb.transact_write_items.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "TransactionCanceledException"}},
        "TransactWriteItems",
    )

    user = User(
        id=None,
        full_name="John",
        email="a@b.com",
        phone_number="123",
        address="addr",
        password_hash="hash",
        society_id=1,
        role=Role.user,
        created_at=datetime.now(),
    )

    with pytest.raises(UserAlreadyExistsError):
        repo.create(user)


def test_create_user_repo_error(repo, dynamodb):
    dynamodb.transact_write_items.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "InternalError"}},
        "TransactWriteItems",
    )

    user = User(
        id=None,
        full_name="John",
        email="a@b.com",
        phone_number="123",
        address="addr",
        password_hash="hash",
        society_id=1,
        role=Role.user,
        created_at=datetime.now(),
    )

    with pytest.raises(UserRepositoryError):
        repo.create(user)


@pytest.mark.asyncio
async def test_become_lender_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "Role": {"S": "buyer"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.become_lender(1)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_become_lender_user_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        with pytest.raises(RuntimeError):
            await repo.become_lender(1)


@pytest.mark.asyncio
async def test_find_all_users_success(repo, dynamodb):
    dynamodb.query.return_value = {
        "Items": [
            {
                "ID": {"N": "1"},
                "FullName": {"S": "John"},
                "Email": {"S": "a@b.com"},
                "PhoneNumber": {"S": "123"},
                "Address": {"S": "addr"},
                "PasswordHash": {"S": "hash"},
                "SocietyID": {"N": "1"},
                "Role": {"S": "user"},
                "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
            }
        ]
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        users = await repo.find_all({})

    assert len(users) == 1
    assert users[0].id == 1


@pytest.mark.asyncio
async def test_find_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "FullName": {"S": "John"},
            "Email": {"S": "a@b.com"},
            "PhoneNumber": {"S": "123"},
            "Address": {"S": "addr"},
            "PasswordHash": {"S": "hash"},
            "SocietyID": {"N": "1"},
            "Role": {"S": "user"},
            "CreatedAt": {"S": "2024-01-01T00:00:00Z"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        user = await repo.find_by_id(1)

    assert user is not None
    assert user.id == 1


@pytest.mark.asyncio
async def test_find_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        user = await repo.find_by_id(1)

    assert user is None


@pytest.mark.asyncio
async def test_delete_by_id_success(repo, dynamodb):
    dynamodb.get_item.return_value = {
        "Item": {
            "ID": {"N": "1"},
            "Role": {"S": "buyer"},
            "Name": {"S": "John"},
            "SocietyID": {"N": "1"},
        }
    }

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.delete_by_id(1)

    dynamodb.transact_write_items.assert_called_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found(repo, dynamodb):
    dynamodb.get_item.return_value = {}

    with patch("asyncio.to_thread", side_effect=lambda function_to_run, **function_kwargs: function_to_run(**function_kwargs)):
        await repo.delete_by_id(1)

    dynamodb.transact_write_items.assert_not_called()
