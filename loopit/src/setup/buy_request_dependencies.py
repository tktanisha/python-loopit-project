
from database.connection import get_dynamodb
from fastapi import Depends
from typing import Annotated
from repository.buy_request_repository import BuyRequestRepo
from repository.product_repository import ProductRepo
from repository.order_repository import OrderRepo
from repository.category_repository import CategoryRepo
from service.buy_request_service import BuyRequestService
from setup.product_dependencies import get_product_repo
from setup.category_dependency import get_category_repo
from setup.order_dependencies import get_order_repo


def get_buyer_request_repo(dynamodb = Depends(get_dynamodb)) -> BuyRequestRepo:
    return BuyRequestRepo(dynamodb)

def get_buyer_request_service(
    buyer_request_repo: Annotated[BuyRequestRepo, Depends(get_buyer_request_repo)],
    product_repo: Annotated[ProductRepo, Depends(get_product_repo)],
       order_repo: Annotated[OrderRepo, Depends(get_order_repo)],
    category_repo: Annotated[CategoryRepo, Depends(get_category_repo)],
) -> BuyRequestService:
    return BuyRequestService(
        product_repo= product_repo,
        order_repo= order_repo,
        buyer_request_repo= buyer_request_repo,
        category_repo= category_repo
    )