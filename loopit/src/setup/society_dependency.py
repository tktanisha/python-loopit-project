from database.connection import get_dynamodb
from service.society_service import SocietyService
from repository.society_repository import SocietyRepo
from fastapi import Depends
from typing import Annotated


def get_society_repo( dynamodb = Depends(get_dynamodb))-> SocietyRepo:
    return SocietyRepo(dynamodb)

def get_society_service(society_repo : Annotated[SocietyRepo, Depends(get_society_repo)])-> SocietyService:
    return SocietyService(society_repo)