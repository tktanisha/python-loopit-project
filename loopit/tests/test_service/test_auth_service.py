import pytest
from unittest.mock import MagicMock, patch

from service.auth.auth_service import AuthServiceImple
from models.user import User
from exception.user import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    AuthServiceError,
    UserNotFoundError,
)


@pytest.fixture
def user_repo():
    return MagicMock()


@pytest.fixture
def service(user_repo):
    return AuthServiceImple(user_repo=user_repo)


@pytest.mark.asyncio
async def test_register_success(service, user_repo, monkeypatch):
    user = MagicMock(spec=User)
    user.email = "test@example.com"
    user.password_hash = "plain"

    user_repo.find_by_email.side_effect = UserNotFoundError()

    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.hash_password",
        lambda pwd: "hashed",
    )

    await service.register(user)

    assert user.password_hash == "hashed"
    user_repo.create.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_register_user_already_exists(service, user_repo):
    user = MagicMock(spec=User)
    user.email = "test@example.com"

    user_repo.find_by_email.return_value = user

    with pytest.raises(UserAlreadyExistsError):
        await service.register(user)


@pytest.mark.asyncio
async def test_register_repo_exception(service, user_repo):
    user = MagicMock(spec=User)
    user.email = "test@example.com"

    user_repo.find_by_email.side_effect = Exception("db error")

    with pytest.raises(AuthServiceError):
        await service.register(user)


@pytest.mark.asyncio
async def test_login_success(service, user_repo, monkeypatch):
    user = MagicMock(spec=User)
    user.id = 1
    user.role = MagicMock(value="buyer")
    user.password_hash = "hashed"

    user_repo.find_by_email.return_value = user

    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.verify_password",
        lambda pwd, hashed: True,
    )
    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.create_token",
        lambda uid, role: "token123",
    )

    token, returned_user = await service.login("a@b.com", "pwd")

    assert token == "token123"
    assert returned_user == user


@pytest.mark.asyncio
async def test_login_user_not_found(service, user_repo):
    user_repo.find_by_email.side_effect = UserNotFoundError()

    with pytest.raises(InvalidCredentialsError):
        await service.login("a@b.com", "pwd")


@pytest.mark.asyncio
async def test_login_invalid_password(service, user_repo, monkeypatch):
    user = MagicMock(spec=User)
    user.password_hash = "hashed"

    user_repo.find_by_email.return_value = user

    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.verify_password",
        lambda pwd, hashed: False,
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login("a@b.com", "pwd")


@pytest.mark.asyncio
async def test_login_token_generation_failure(service, user_repo, monkeypatch):
    user = MagicMock(spec=User)
    user.id = 1
    user.role = MagicMock(value="buyer")
    user.password_hash = "hashed"

    user_repo.find_by_email.return_value = user

    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.verify_password",
        lambda pwd, hashed: True,
    )
    monkeypatch.setattr(
        "helpers.auth_helper.AuthHelper.create_token",
        lambda *_: (_ for _ in ()).throw(Exception("jwt error")),
    )

    with pytest.raises(AuthServiceError):
        await service.login("a@b.com", "pwd")
