
import logging
from typing import List
from datetime import datetime
from repository.order_repository import OrderRepo
from repository.product_repository import ProductRepo
from repository.return_request_repository import ReturnRequestRepo
from models.return_request import ReturnRequest
from models.enums.return_req_status import ReturnStatus
from models.enums.order_status import OrderStatus

logger = logging.getLogger(__name__)


class ReturnRequestService:
    def __init__(self, order_repo:OrderRepo, product_repo:ProductRepo, return_request_repo:ReturnRequestRepo):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.return_request_repo = return_request_repo

    async def create_return_request(self, user_id: int, order_id: int) -> None:
        try:
            order = await self.order_repo.get_order_by_id(order_id)
            if order is None:
                raise RuntimeError("order not found")
            if order.status != OrderStatus.InUse:
                raise RuntimeError("order is not in 'in_use' status")

            product_resp = await self.product_repo.find_by_id(order.product_id)
            if product_resp is None:
                raise RuntimeError("product not found")
            if int(product_resp.product.lender_id) != int(user_id):
                raise RuntimeError("user is not lender of the order's product")

            rr = ReturnRequest(
                order_id=order_id,
                requested_by=user_id,
                status=ReturnStatus.Pending,
                created_at=datetime.now(),
            )

            await self.order_repo.update_order_status(order_id, OrderStatus.ReturnRequested.value)
            await self.return_request_repo.create_return_request(rr)
        except Exception as e:
            logger.exception("failed in service create_return_request")
            raise e

    async def update_return_request_status(self, user_id: int, req_id: int, new_status: ReturnStatus) -> None:
        try:
            if new_status not in (ReturnStatus.Approved, ReturnStatus.Rejected):
                raise RuntimeError("invalid status update")

            req = await self.return_request_repo.get_return_request_by_id(req_id)
            if req is None:
                raise RuntimeError("return request not found")
            if req.status != ReturnStatus.Pending:
                raise RuntimeError("return request is not in pending status")

            order = await self.order_repo.get_order_by_id(req.order_id)
            if order is None:
                raise RuntimeError("order not found")
            if int(order.user_id) != int(user_id):
                raise RuntimeError("user does not own this order")

            await self.return_request_repo.update_return_request_status(req.id, new_status.value)
        except Exception as e:
            logger.exception("failed in service update_return_request_status")
            raise e

    async def get_pending_return_requests(self, user_id: int) -> List[ReturnRequest]:
        try:
            all_requests = await self.return_request_repo.get_all_return_requests([ReturnStatus.Pending.value])
            user_requests: List[ReturnRequest] = []
            for req in all_requests:
                order = await self.order_repo.get_order_by_id(req.order_id)
                if order and int(order.user_id) == int(user_id):
                    user_requests.append(req)
            return user_requests
        except Exception as e:
            logger.exception("failed in service get_pending_return_requests")
            raise e
