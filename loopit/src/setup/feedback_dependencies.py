
from fastapi import Depends
from typing import Annotated
from database.connection import get_dynamodb
from repository.feedback_repository import FeedbackRepo
from service.feedback_service import FeedbackService

def get_feedback_repo(dynamodb = Depends(get_dynamodb)) -> FeedbackRepo:
    return FeedbackRepo(dynamodb)

def get_feedback_service(feedback_repo: Annotated[FeedbackRepo, Depends(get_feedback_repo)]) -> FeedbackService:
    return FeedbackService(feedback_repo)
