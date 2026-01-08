
from database.connection import get_dynamodb
from setup.product_dependencies import get_product_repo
from repository.order_repository import OrderRepo
from repository.product_repository import ProductRepo
from fastapi import Depends
from typing import Annotated

def get_order_repo(
        product_repo: Annotated[ProductRepo, Depends(get_product_repo)],
        dynamodb = Depends(get_dynamodb)
          ) -> OrderRepo:
    return OrderRepo(
        dynamodb = dynamodb,
        product_repo= product_repo
          )

