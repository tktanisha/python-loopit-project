
from fastapi import Depends
from typing import Annotated
from database.connection import get_dynamodb
from setup.product_dependencies import get_product_repo
from setup.order_dependencies import get_order_repo
from repository.feedback_repository import FeedbackRepo
from service.feedback_service import FeedbackService
from repository.product_repository import ProductRepo
from repository.order_repository import OrderRepo


def get_feedback_repo(dynamodb = Depends(get_dynamodb)) -> FeedbackRepo:
    return FeedbackRepo(dynamodb)

def get_feedback_service(
        feedback_repo: Annotated[FeedbackRepo, Depends(get_feedback_repo)],
        product_repo:Annotated[ProductRepo, Depends(get_product_repo)],
        order_repo: Annotated[OrderRepo, Depends(get_order_repo)]) -> FeedbackService:
    return FeedbackService(
        feedback_repo= feedback_repo,
        product_repo= product_repo,
        order_repo= order_repo
    )
