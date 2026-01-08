
from fastapi import Depends
from typing import Annotated
from repository.user.user_repository import UserDynamoRepo
from service.auth.auth_service import AuthServiceImple
from service.auth.auth_interface import AuthService
from database.connection import get_dynamodb


#it can create a new DynamoDB client per request
# def get_dynamodb():
#     return boto3.client("dynamodb")


# def get_auth_service( user_repo=Depends(get_user_repo)) -> AuthService:
#     return AuthServiceImple(user_repo)


def get_user_repo(
    dynamodb = Depends(get_dynamodb)
):
    return UserDynamoRepo(dynamodb)


def get_auth_service( 
        user_repo: Annotated[UserDynamoRepo, Depends(get_user_repo)]) -> AuthService:
    return AuthServiceImple(user_repo)
