
from fastapi import status
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.return_request_service import ReturnRequestService


async def get_pending_return_requests(user_ctx, return_request_service: ReturnRequestService):
 
    try:
        requests = await return_request_service.get_pending_return_requests(user_ctx.id)
        data = (
            [r.model_dump() for r in requests]
            if hasattr(requests, "__iter__") and hasattr(next(iter(requests), None), "model_dump")
            else requests
        )
    except StopIteration:
        # empty iterable case
        data = []
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="could not fetch return requests",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )

async def create_return_request(order_id: int, user_ctx, return_request_service: ReturnRequestService):

    try:
        await return_request_service.create_return_request(user_ctx.id, order_id)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="could not create return request",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="Return request created successfully",
    )

async def update_return_request_status(request_id: int, status: str, user_ctx, return_request_service: ReturnRequestService):

    # Optional enum validation (if you have an Enum class):
    # try:
    #     parsed_status = ReturnRequestStatus(status)
    # except Exception as e:
    #     return write_error_response(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         error="invalid status value",
    #         details=str(e),
    #     )

    try:
        # If service handles parsing/validation, pass status string directly
        await return_request_service.update_return_request_status(user_ctx.id, request_id, status)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="could not update return request",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="Return request status updated successfully",
    )
