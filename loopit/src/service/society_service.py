
import logging
from typing import List, Optional
from datetime import datetime
from models.society import Society  
from repository.society_repository import SocietyRepo  

logger = logging.getLogger(__name__)


class SocietyService:
    def __init__(self, society_repo: SocietyRepo):
        self.society_repo = society_repo

    async def get_all_societies(self) -> List[Society]:
        try:
            societies: List[Society] = await self.society_repo.find_all()
            return societies
        except Exception as e:
            logger.exception("failed in service: get_all_societies")
            raise e

    async def create_society(self, name: str, location: str, pincode: str) -> None:
        society = Society(
            name=name,
            location=location,
            pincode=pincode,
            created_at=datetime.now
        )

        try:
            await self.society_repo.create(society)
        except Exception as e:
            logger.exception("failed in service: create_society")
            raise e

    async def update_society(self, id: int, name: str, location: str, pincode: str) -> None:
        try:
            society: Optional[Society] = await self.society_repo.find_by_id(id)
        except Exception as e:
            logger.exception("failed in service: find_by_id for update_society")
            raise e

        if society is None:
            raise RuntimeError(f"society {id} does not exist")

        society.name = name
        society.location = location
        society.pincode = pincode

        try:
            await self.society_repo.update(society)
        except Exception as e:
            logger.exception("failed in service: update_society")
            raise e

    async def delete_society(self, id: int) -> None:
     
       
        try:
            society: Optional[Society] = await self.society_repo.find_by_id(id)
        except Exception as e:
            logger.exception("failed in service: find_by_id before delete_society")
            raise e

        if society is None:
            raise RuntimeError(f"society {id} does not exist")

        try:
            await self.society_repo.delete(id)
        except Exception as e:
            logger.exception("failed in service: delete_society")
            raise e
