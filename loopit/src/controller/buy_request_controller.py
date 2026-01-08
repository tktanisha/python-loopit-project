
# controller/buyer_request_controller.py
from fastapi import status
from typing import Optional, List
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.buy_request_service import BuyRequestService
from service.product_service import ProductService
from models.enums.buy_request import BuyRequestStatus



async def create_buyer_request(
    product_id: int,
    buyer_request_service: BuyRequestService,
    user_ctx,
):
   
    try:
        await buyer_request_service.create_buyer_request(product_id, user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="failed to create buyer request",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="buyer request created successfully",
    )


async def update_buyer_request_status(
    request_id: int,
    status_str: str,
    buyer_request_service: BuyRequestService,
    user_ctx,
):
 
    
    try:

        parsed_status = BuyRequestStatus(status_str)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=f"invalid status value= {parsed_status}",
            details=str(e),
        )

    try:
        await buyer_request_service.update_buyer_request_status(request_id, status_str, user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="failed to update status",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="buyer request status updated successfully",
    )


async def get_all_buyer_requests(
    product_id: Optional[int],
    status_str: Optional[str],
    buyer_request_service: BuyRequestService,
    product_service: ProductService,
):
   
    try:
        status_filter: List[str] = status_str.split(",") if status_str else []
        requests = await buyer_request_service.get_all_buyer_requests(product_id, status_filter)

        responses = []
        for r in requests:
            try:
                product = await product_service.get_product_by_id(r.product_id)
                buy_request_data = r.model_dump() if hasattr(r, "model_dump") else r
                product_data = product.model_dump() if hasattr(product, "model_dump") else product
                responses.append({
                    "buy_request": buy_request_data,
                    "product": product_data,
                })
            except Exception as e:
                return write_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error="failed to fetch buyer requests",
                details=str(e),
        )          

    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch buyer requests",
            details=str(e),
        )
    
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data= responses,
        message="buyer request fetched successfully",
    )
