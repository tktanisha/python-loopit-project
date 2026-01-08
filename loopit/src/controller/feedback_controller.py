
from fastapi import status
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.feedback_service import FeedbackService
from schemas.feedback import FeedbackRequest

async def give_feedback(feedback: FeedbackRequest, feedback_service: FeedbackService, user_ctx):
    try:
        await feedback_service.give_feedback(
            order_id=feedback.order_id,
            feedback_text=feedback.feedback_text,
            rating=feedback.rating,
            user_ctx=user_ctx,
        )
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="failed to give feedback",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Feedback given successfully",
    )

async def get_all_given_feedbacks(feedback_service: FeedbackService, user_ctx):
    try:
        feedbacks = await feedback_service.get_all_given_feedbacks(user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch given feedbacks",
            details=str(e),
        )
    data = feedbacks if not hasattr(feedbacks, "model_dump") else [f.model_dump() for f in feedbacks]
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )

async def get_all_received_feedbacks(feedback_service: FeedbackService, user_ctx):
    try:
        feedbacks = await feedback_service.get_all_received_feedbacks(user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch received feedbacks",
            details=str(e),
        )
    data = feedbacks if not hasattr(feedbacks, "model_dump") else [f.model_dump() for f in feedbacks]
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )
