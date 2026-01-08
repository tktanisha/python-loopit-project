
from fastapi import Depends
from typing import Annotated
from database.connection import get_dynamodb
from setup.product_dependencies import get_product_repo
from repository.order_repository import OrderRepo
from repository.product_repository import ProductRepo
from repository.return_request_repository import ReturnRequestRepo
from service.return_request_service import ReturnRequestService




def get_return_request_repo(dynamodb = Depends(get_dynamodb)) -> ReturnRequestRepo:
    return ReturnRequestRepo(dynamodb)

