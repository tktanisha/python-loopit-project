
from database.connection import get_dynamodb
from fastapi import Depends
from typing import Annotated
from service.product_service import ProductService
from repository.product_repository import ProductRepo
from repository.category_repository import CategoryRepo
from repository.user.user_interface import UserRepo
from setup.dependencies import get_user_repo
from setup.category_dependency import get_category_repo

def get_product_repo(
        user_repo:Annotated[UserRepo, Depends(get_user_repo)],
        category_repo: Annotated[CategoryRepo, Depends(get_category_repo)],
        dynamodb=Depends(get_dynamodb),
        ) -> ProductRepo:
    return ProductRepo(
        dynamodb=dynamodb,
        category_repo= category_repo,
        user_repo= user_repo
        )

def get_product_service(
        product_repo: Annotated[ProductRepo, Depends(get_product_repo)],
        user_repo:Annotated[UserRepo,Depends(get_user_repo)]) -> ProductService:
    return ProductService(
        product_repo = product_repo,
        user_repo = user_repo
        )
