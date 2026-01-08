
# controller/order_controller.py
from fastapi import status
from typing import Optional, List
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.order_service import OrderService
from service.product_service import ProductService
from models.enums.order_status import OrderStatus
from schemas.orders import OrderResponse,OrderSchema,order_to_schema,product_to_response

async def get_order_history(user_ctx, status_str: Optional[str], order_service: OrderService, product_service: ProductService):
    try:
        filter_status: List[OrderStatus] = []
        if status_str:
            try:
                filter_status = [OrderStatus(status_str)]
                print("filter status=", filter_status)
            except Exception as e:
                return write_error_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error="invalid status filter",
                    details=str(e),
                )
        orders = await order_service.get_order_history(user_ctx=user_ctx, filter_statuses =filter_status)
        responses = []
        for o in orders:
            try:
                p = await product_service.get_product_by_id(o.product_id)
                responses.append(OrderResponse(
                        order=order_to_schema(o),
                        product=product_to_response(p),
                    ))
            except Exception:
                continue
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch order history",
            details=str(e),
        )
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in responses]
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )

async def mark_order_as_returned(order_id: int, order_service: OrderService, user_ctx):
    try:
        await order_service.mark_order_as_returned(order_id=order_id, user_ctx=user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="failed to update order status",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="order status updated successfully",
    )

async def get_all_approved_awaiting_orders(order_service: OrderService, product_service: ProductService, user_ctx):
    try:
        orders = await order_service.get_all_approved_awaiting_orders(user_ctx=user_ctx)
        responses = []
        for o in orders:
            try:
                p = await product_service.get_product_by_id(o.product_id)
                responses.append(OrderResponse(order=o, product=p))
            except Exception:
                continue
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch approved awaiting orders",
            details=str(e),
        )
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in responses]
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )

async def get_lender_orders(order_service: OrderService, product_service: ProductService, user_ctx):
    try:
        orders:OrderSchema = await order_service.get_lender_orders(user_ctx=user_ctx)
        responses:List[OrderResponse] = []
        for o in orders:
            try:
                p = await product_service.get_product_by_id(o.product_id)
                responses.append(
                    OrderResponse(
                        order=order_to_schema(o),
                        product=product_to_response(p),
                    )
                )

            except Exception:
                continue
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch lender orders",
            details=str(e),
        )
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in responses]
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data= data,
    )
