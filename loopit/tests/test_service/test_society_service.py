import pytest
from unittest.mock import AsyncMock, MagicMock

from service.society_service import SocietyService
from models.society import Society


@pytest.fixture
def society_repo():
    return AsyncMock()


@pytest.fixture
def service(society_repo):
    return SocietyService(society_repo=society_repo)


@pytest.mark.asyncio
async def test_get_all_societies_success(service, society_repo):
    society_repo.find_all.return_value = ["s1", "s2"]
    result = await service.get_all_societies()
    assert result == ["s1", "s2"]
    society_repo.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_societies_exception(service, society_repo):
    society_repo.find_all.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.get_all_societies()


@pytest.mark.asyncio
async def test_create_society_success(service, society_repo):
    await service.create_society("Society A", "Location A", "123456")
    society_repo.create.assert_called_once()
    society = society_repo.create.call_args[0][0]
    assert isinstance(society, Society)
    assert society.name == "Society A"
    assert society.location == "Location A"
    assert society.pincode == "123456"


@pytest.mark.asyncio
async def test_create_society_exception(service, society_repo):
    society_repo.create.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.create_society("Society A", "Location A", "123456")


@pytest.mark.asyncio
async def test_update_society_success(service, society_repo):
    society = MagicMock(spec=Society)
    society_repo.find_by_id.return_value = society

    await service.update_society(1, "New Name", "New Location", "654321")

    assert society.name == "New Name"
    assert society.location == "New Location"
    assert society.pincode == "654321"
    society_repo.update.assert_called_once_with(society)


@pytest.mark.asyncio
async def test_update_society_not_found(service, society_repo):
    society_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.update_society(1, "Name", "Loc", "000000")


@pytest.mark.asyncio
async def test_update_society_find_exception(service, society_repo):
    society_repo.find_by_id.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.update_society(1, "Name", "Loc", "000000")


@pytest.mark.asyncio
async def test_delete_society_success(service, society_repo):
    society_repo.find_by_id.return_value = MagicMock(spec=Society)
    await service.delete_society(1)
    society_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_society_not_found(service, society_repo):
    society_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        await service.delete_society(1)


@pytest.mark.asyncio
async def test_delete_society_find_exception(service, society_repo):
    society_repo.find_by_id.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await service.delete_society(1)
