from database.connection import get_dynamodb
from service.category_service import CategoryService
from repository.category_repository import CategoryRepo
from fastapi import Depends
from typing import Annotated


def get_category_repo( dynamodb = Depends(get_dynamodb))-> CategoryRepo:
    return CategoryRepo(dynamodb)

def get_category_service(category_repo : Annotated[CategoryRepo, Depends(get_category_repo)])-> CategoryService:
    return CategoryService(category_repo)