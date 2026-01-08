
from fastapi import Depends
from typing import Annotated
from service.user_service import UserService
from repository.user.user_interface import UserRepo
from setup.dependencies import get_user_repo  # you mentioned this exists

def get_user_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)]
) -> UserService:
    return UserService(user_repo)
