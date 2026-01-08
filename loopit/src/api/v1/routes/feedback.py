
from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
from setup.feedback_dependencies import get_feedback_service
from service.feedback_service import FeedbackService
from controller import feedback_controller as controller
from schemas.feedback import FeedbackRequest

router = APIRouter(dependencies=[Depends(AuthHelper.verify_jwt)])

@router.post(ApiPaths.CREATE_FEEDBACK, status_code=status.HTTP_201_CREATED)
async def give_feedback(
    payload: FeedbackRequest,
    request: Request,
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    user_ctx = request.state.user
    return await controller.give_feedback(
        feedback=payload,
        feedback_service=feedback_service,
        user_ctx=user_ctx,
    )

# @router.get(ApiPaths.GET_GIVEN_FEEDBACKS, status_code=status.HTTP_200_OK)
# async def get_all_given_feedbacks(
#     request: Request,
#     feedback_service: FeedbackService = Depends(get_feedback_service),
# ):
#     user_ctx = request.state.user
#     return await controller.get_all_given_feedbacks(
#         feedback_service=feedback_service,
#         user_ctx=user_ctx,
#     )

# @router.get(ApiPaths.GET_RECEIVED_FEEDBACKS, status_code=status.HTTP_200_OK)
# async def get_all_received_feedbacks(
#     request: Request,
#     feedback_service: FeedbackService = Depends(get_feedback_service),
# ):
#     user_ctx = request.state.user
#     return await controller.get_all_received_feedbacks(
#         feedback_service=feedback_service,
#         user_ctx=user_ctx,
#     )
