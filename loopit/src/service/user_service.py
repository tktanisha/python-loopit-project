
# services/user_service.py
import logging
from typing import Optional, Dict, Any, List
from repository.user.user_interface import UserRepo

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repo:UserRepo):
        self.user_repo = user_repo

    async def become_lender(self, user_ctx) -> None:
        try:
            if user_ctx is None:
                raise RuntimeError("user context missing")

            role_val = getattr(user_ctx, "role", None) if not isinstance(user_ctx, dict) else user_ctx.get("role")
            if str(role_val).lower() == "lender":
                raise RuntimeError("user is already a lender")

            user_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if user_id is None or int(user_id) <= 0:
                raise RuntimeError("invalid user id")

            await self.user_repo.become_lender(int(user_id))
        except Exception as e:
            logger.exception("failed in service become_lender")
            raise e

    async def get_all_users(self, filters: Optional[Dict[str, Any]]) -> List:
        try:
            filters = filters or {}
            users = await self.user_repo.find_all(filters)
            return users
        except Exception as e:
            logger.exception("failed in service get_all_users")
            raise e

    async def get_user_by_id(self, user_id: int):
        try:
            if int(user_id) <= 0:
                raise RuntimeError("user ID must be a positive integer")
            user = await self.user_repo.find_by_id(int(user_id))
            return user
        except Exception as e:
            logger.exception("failed in service get_user_by_id")
            raise e

    async def delete_user_by_id(self, user_id: int) -> None:
        try:
            if int(user_id) <= 0:
                raise RuntimeError("user ID must be a positive integer")
            await self.user_repo.delete_by_id(int(user_id))
        except Exception as e:
            logger.exception("failed in service delete_user_by_id")
            raise e
