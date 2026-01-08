from fastapi import Depends
from typing import Annotated
from setup.order_dependencies import get_order_repo
from setup.product_dependencies import get_product_repo
from setup.return_request_dependencies import get_return_request_repo
from repository.order_repository import OrderRepo
from repository.product_repository import ProductRepo
from repository.return_request_repository import ReturnRequestRepo
from service.order_service import OrderService

def get_order_service(
    order_repo: Annotated[OrderRepo, Depends(get_order_repo)],
    product_repo: Annotated[ProductRepo, Depends(get_product_repo)],
    return_request_repo: Annotated[ReturnRequestRepo, Depends(get_return_request_repo)],
    
) -> OrderService:
    return OrderService(
        order_repo=order_repo,
        product_repo=product_repo,
        return_request_repo=return_request_repo,
    )
