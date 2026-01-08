
# api/order_routes.py
from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from service.order_service import OrderService
from service.product_service import ProductService
from setup.order_service_dependencies import get_order_service
from setup.product_dependencies import get_product_service
from controller import order_controller as controller
from helpers.api_paths import ApiPaths

router = APIRouter()

@router.get(ApiPaths.GET_ORDER_HISTORY, status_code=status.HTTP_200_OK, dependencies=[Depends(AuthHelper.verify_jwt)])
async def get_order_history(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    product_service: ProductService = Depends(get_product_service),
):
    user_ctx = request.state.user
    return await controller.get_order_history(
        user_ctx=user_ctx,
        status_str=request.query_params.get("status"),
        order_service=order_service,
        product_service=product_service,
    )

@router.patch(ApiPaths.RETURN_ORDER, status_code=status.HTTP_200_OK, dependencies=[Depends(AuthHelper.verify_jwt)])
async def mark_order_as_returned(
    orderId: int,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
):
    user_ctx = request.state.user
    return await controller.mark_order_as_returned(
        order_id=orderId,
        order_service=order_service,
        user_ctx=user_ctx,
    )

@router.get(ApiPaths.GET_APPROVED_AWAITING_ORDERS, status_code=status.HTTP_200_OK, dependencies=[Depends(AuthHelper.verify_jwt)])
async def get_all_approved_awaiting_orders(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    product_service: ProductService = Depends(get_product_service),
):
    user_ctx = request.state.user
    return await controller.get_all_approved_awaiting_orders(
        order_service=order_service,
        product_service=product_service,
        user_ctx=user_ctx,
    )

@router.get(ApiPaths.GET_LENDER_ORDERS, status_code=status.HTTP_200_OK, dependencies=[Depends(AuthHelper.verify_jwt)])
async def get_lender_orders(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    product_service: ProductService = Depends(get_product_service),
):
    user_ctx = request.state.user
    return await controller.get_lender_orders(
        order_service=order_service,
        product_service=product_service,
        user_ctx=user_ctx,
    )
