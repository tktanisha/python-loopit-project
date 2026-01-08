
from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
from setup.buy_request_dependencies import get_buyer_request_service
from setup.product_dependencies import get_product_service
from service.buy_request_service import BuyRequestService
from service.product_service import ProductService
from controller import buy_request_controller as controller
from schemas.buy_request import BuyRequestPayload, UpdateBuyerRequestStatus

from typing import Optional

router = APIRouter(dependencies=[Depends(AuthHelper.verify_jwt)])

@router.post(ApiPaths.CREATE_BUYER_REQUEST, status_code=status.HTTP_201_CREATED, )
async def create_buyer_request(
    payload: BuyRequestPayload,
    request: Request,
    buyer_request_service: BuyRequestService = Depends(get_buyer_request_service),
):
    user_ctx = request.state.user
    return await controller.create_buyer_request(
        product_id=payload.product_id,
        buyer_request_service=buyer_request_service,
        user_ctx=user_ctx,
    )

@router.get(ApiPaths.GET_BUYER_REQUESTS, status_code=status.HTTP_200_OK)
async def get_all_buyer_requests(
    request : Request,
    buyer_request_service: BuyRequestService = Depends(get_buyer_request_service),
    product_service: ProductService = Depends(get_product_service),
):
    return await controller.get_all_buyer_requests(
        product_id= (request.query_params.get("product_id")),
        status_str = request.query_params.get("status"),
        buyer_request_service=buyer_request_service,
        product_service=product_service,
    )

@router.patch(ApiPaths.UPDATE_BUYER_REQUEST_STATUS, status_code=status.HTTP_200_OK, dependencies=[Depends(AuthHelper.verify_jwt)])
async def update_buyer_request_status(
    requestId: int,
    payload: UpdateBuyerRequestStatus,
    request: Request,
    buyer_request_service: BuyRequestService = Depends(get_buyer_request_service),
):
    
    return await controller.update_buyer_request_status(
        request_id=requestId,
        status_str=payload.status,
        buyer_request_service=buyer_request_service,
        user_ctx= request.state.user,
    )
