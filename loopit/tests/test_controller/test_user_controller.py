import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import status

from controller.user_controller import (
    become_lender,
    get_all_users,
    get_user_by_id,
    delete_user_by_id,
)


@pytest.mark.asyncio
async def test_become_lender_success_dict_ctx():
    service = MagicMock()
    service.become_lender = AsyncMock(return_value=None)

    user_ctx = {"user_id": 1, "role": "user"}

    resp = await become_lender(service, user_ctx)

    service.become_lender.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK
    assert user_ctx["role"] == "lender"


@pytest.mark.asyncio
async def test_become_lender_unauthorized():
    service = MagicMock()

    resp = await become_lender(service, None)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_become_lender_failure():
    service = MagicMock()
    service.become_lender = AsyncMock(side_effect=Exception("fail"))

    user_ctx = {"user_id": 1, "role": "user"}

    resp = await become_lender(service, user_ctx)

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_all_users_success():
    service = MagicMock()
    service.get_all_users = AsyncMock(return_value=[])

    admin_ctx = {"role": "admin"}

    resp = await get_all_users(
        search=None,
        role=None,
        society_id=None,
        user_service=service,
        user_ctx=admin_ctx,
    )

    service.get_all_users.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_users_not_admin():
    service = MagicMock()
    user_ctx = {"role": "user"}

    resp = await get_all_users(
        search=None,
        role=None,
        society_id=None,
        user_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_all_users_unauthorized():
    service = MagicMock()

    resp = await get_all_users(
        search=None,
        role=None,
        society_id=None,
        user_service=service,
        user_ctx=None,
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_by_id_success():
    service = MagicMock()
    service.get_user_by_id = AsyncMock(return_value={"id": 1, "name": "abc"})

    admin_ctx = {"role": "admin"}

    resp = await get_user_by_id(
        id=1,
        user_service=service,
        user_ctx=admin_ctx,
    )

    service.get_user_by_id.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    service = MagicMock()
    service.get_user_by_id = AsyncMock(return_value=None)

    admin_ctx = {"role": "admin"}

    resp = await get_user_by_id(
        id=99,
        user_service=service,
        user_ctx=admin_ctx,
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_by_id_forbidden():
    service = MagicMock()
    user_ctx = {"role": "user"}

    resp = await get_user_by_id(
        id=1,
        user_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_by_id_success():
    service = MagicMock()
    service.delete_user_by_id = AsyncMock(return_value=None)

    admin_ctx = {"role": "admin"}

    resp = await delete_user_by_id(
        id=1,
        user_service=service,
        user_ctx=admin_ctx,
    )

    service.delete_user_by_id.assert_awaited_once()
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_user_by_id_not_admin():
    service = MagicMock()
    user_ctx = {"role": "user"}

    resp = await delete_user_by_id(
        id=1,
        user_service=service,
        user_ctx=user_ctx,
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_by_id_failure():
    service = MagicMock()
    service.delete_user_by_id = AsyncMock(side_effect=Exception("fail"))

    admin_ctx = {"role": "admin"}

    resp = await delete_user_by_id(
        id=1,
        user_service=service,
        user_ctx=admin_ctx,
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
