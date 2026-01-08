
import logging
from typing import Optional, List
from datetime import datetime,timezone
from models.buy_request import BuyingRequest
from models.orders import Order
from models.enums.buy_request import BuyRequestStatus
from models.enums.order_status import OrderStatus
from repository.product_repository import ProductRepo
from repository.order_repository import OrderRepo
from repository.category_repository import CategoryRepo
from repository.buy_request_repository import BuyRequestRepo


logger = logging.getLogger(__name__)


class BuyRequestService:
    def __init__(
        self,
        product_repo : ProductRepo,
        buyer_request_repo:BuyRequestRepo,
        category_repo:CategoryRepo,
        order_repo: OrderRepo,
    ):
        self.product_repo = product_repo
        self.buyer_request_repo = buyer_request_repo
        self.category_repo = category_repo
        self.order_repo = order_repo

    async def create_buyer_request(self, product_id: int, user_ctx) -> None:
        try:
            product_resp = await self.product_repo.find_by_id(product_id)
            if product_resp is None:
                raise RuntimeError("product not found")
            
            if not bool(product_resp.product.is_available):
                raise RuntimeError("product not available")

            requester_id = user_ctx.get("user_id")
            
            if requester_id is None or int(requester_id) <= 0:
                raise RuntimeError("invalid request id")

            if int(product_resp.product.lender_id) == int(requester_id):
                raise RuntimeError("lender cannot create a buying request for their own product")

            #checking if biy request already exist on this product
            statuses = [BuyRequestStatus.Pending.value]
            existing_requests: List[BuyingRequest] = await self.buyer_request_repo.get_all_buyer_requests(
                product_id, statuses
            )
            for req in existing_requests:
     
                if int(req.requested_by) == int(requester_id):
                    raise RuntimeError("a pending or approved request already exists")

            new_request = BuyingRequest(
                product_id=product_id,
                requested_by=int(requester_id),
                status=BuyRequestStatus.Pending.value,
                created_at=datetime.now,
            )
            await self.buyer_request_repo.create_buyer_request(new_request)

        except Exception as e:
            logger.exception("failed in service create_buyer_request")
            raise e

    async def update_buyer_request_status(self, request_id: int, updated_status: str, user_ctx) -> None:
        try:
            role_val = user_ctx.get("role")
            
            if role_val not in ("lender",):  
                raise RuntimeError("unauthorized: only lenders can update request status")

            if updated_status not in (BuyRequestStatus.Approved.value, BuyRequestStatus.Rejected.value):
                raise RuntimeError("invalid status: only 'approved' or 'rejected' allowed")

            all_requests: List[BuyingRequest] = await self.buyer_request_repo.get_all_buyer_requests()
            req: Optional[BuyingRequest] = next((r for r in all_requests if int(getattr(r, "id", 0)) == int(request_id)), None)
            if req is None:
                raise RuntimeError("buyer request not found")

            if updated_status == BuyRequestStatus.Rejected.value:
                await self.buyer_request_repo.update_status_buyer_request(request_id, BuyRequestStatus.Rejected.value)
                return

            product_resp = await self.product_repo.find_by_id(req.product_id)
            if product_resp is None:
                raise RuntimeError("product not found")

            category = await self.category_repo.find_by_id(int(product_resp.category.id))
            if category is None:
                raise RuntimeError("category not found")

            new_order = Order(
                product_id=req.product_id,
                user_id=req.requested_by,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.fromtimestamp(0, tz=timezone.utc),
                total_amount=float(getattr(category, "price", 0.0)),
                security_amount=float(getattr(category, "security", 0.0)),
                status=OrderStatus.InUse.value,
                created_at=datetime.now,
            )

            await self.order_repo.create_order(new_order)
            await self.buyer_request_repo.update_status_buyer_request(request_id, BuyRequestStatus.Approved.value)

        except Exception as e:
            logger.exception("failed in service update_buyer_request_status")
            raise e

    async def get_all_buyer_requests(
        self,
        product_id: Optional[int],
        filter_statuses: Optional[List[str]],
    ) -> List[BuyingRequest]:
        try:
            requests = await self.buyer_request_repo.get_all_buyer_requests(product_id, filter_statuses)
            return requests
        except Exception as e:
            logger.exception("failed in service get_all_buyer_requests")
            raise e
