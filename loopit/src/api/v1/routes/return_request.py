
# api/return_request_routes.py
from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
from setup.return_request_service import get_return_request_service
from service.return_request_service import ReturnRequestService
from controller import return_request_controller as controller
from schemas.return_request import ReturnRequestPayload, ReturnRequestSchema, ReturnRequestStatusUpdate

router = APIRouter(dependencies=[Depends(AuthHelper.verify_jwt)])

@router.get(ApiPaths.GET_RETURN_REQUESTS, status_code=status.HTTP_200_OK)
async def get_return_requests(
    request: Request,
    return_request_service: ReturnRequestService = Depends(get_return_request_service),
):
    user_ctx = request.state.user
    return await controller.get_pending_return_requests(
        user_ctx=user_ctx,
        return_request_service=return_request_service,
    )

@router.post(ApiPaths.CREATE_RETURN_REQUEST, status_code=status.HTTP_201_CREATED)
async def create_return_request(
    payload: ReturnRequestPayload,
    request: Request,
    return_request_service: ReturnRequestService = Depends(get_return_request_service),
):
    user_ctx = request.state.user
    return await controller.create_return_request(
        order_id=payload.order_id,
        user_ctx=user_ctx,
        return_request_service=return_request_service,
    )

@router.patch(ApiPaths.UPDATE_RETURN_REQUEST_STATUS, status_code=status.HTTP_200_OK)
async def update_return_request_status(
    requestId: int,
    payload: ReturnRequestStatusUpdate,
    request: Request,
    return_request_service: ReturnRequestService = Depends(get_return_request_service),
):
    user_ctx = request.state.user
    return await controller.update_return_request_status(
        request_id=requestId,
        status_str=payload.status,
        user_ctx=user_ctx,
        return_request_service=return_request_service,
    )
