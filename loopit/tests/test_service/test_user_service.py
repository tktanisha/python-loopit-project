import pytest
from unittest.mock import AsyncMock

from service.user_service import UserService


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def service(user_repo):
    return UserService(user_repo=user_repo)


@pytest.mark.asyncio
async def test_become_lender_success(service, user_repo):
    user_ctx = {"user_id": 1, "role": "buyer"}
    await service.become_lender(user_ctx)
    user_repo.become_lender.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_become_lender_user_ctx_missing(service):
    with pytest.raises(RuntimeError):
        await service.become_lender(None)


@pytest.mark.asyncio
async def test_become_lender_already_lender(service):
    with pytest.raises(RuntimeError):
        await service.become_lender({"user_id": 1, "role": "lender"})


@pytest.mark.asyncio
async def test_become_lender_invalid_user_id(service):
    with pytest.raises(RuntimeError):
        await service.become_lender({"user_id": 0, "role": "buyer"})


@pytest.mark.asyncio
async def test_get_all_users_success(service, user_repo):
    user_repo.find_all.return_value = ["u1", "u2"]
    result = await service.get_all_users(None)
    assert result == ["u1", "u2"]
    user_repo.find_all.assert_called_once_with({})


@pytest.mark.asyncio
async def test_get_all_users_exception(service, user_repo):
    user_repo.find_all.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.get_all_users({})


@pytest.mark.asyncio
async def test_get_user_by_id_success(service, user_repo):
    user_repo.find_by_id.return_value = "user"
    result = await service.get_user_by_id(1)
    assert result == "user"
    user_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_user_by_id_invalid_id(service):
    with pytest.raises(RuntimeError):
        await service.get_user_by_id(0)


@pytest.mark.asyncio
async def test_delete_user_by_id_success(service, user_repo):
    await service.delete_user_by_id(1)
    user_repo.delete_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_user_by_id_invalid_id(service):
    with pytest.raises(RuntimeError):
        await service.delete_user_by_id(0)
