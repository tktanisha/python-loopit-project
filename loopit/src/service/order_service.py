
import logging
from typing import List
from models.enums.order_status import OrderStatus
from repository.order_repository import OrderRepo
from repository.product_repository import ProductRepo
from repository.return_request_repository import ReturnRequestRepo
from models.enums.user import Role
from models.orders import Order

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, order_repo:OrderRepo , product_repo:ProductRepo, return_request_repo:ReturnRequestRepo,):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.return_request_repo = return_request_repo

    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> None:
        try:
            order = await self.order_repo.get_order_by_id(order_id)
            if order is None:
                raise RuntimeError("order not found")
            if new_status == OrderStatus.Returned and order.status != OrderStatus.ReturnRequested:
                raise RuntimeError("order must be in return_requested status to mark as returned")
            await self.order_repo.update_order_status(order_id, new_status.value)
        except Exception as e:
            logger.exception("failed in service update_order_status")
            raise e

    async def get_order_history(self, user_ctx, filter_statuses: List[OrderStatus]) -> List[Order]:
        print("in the service-------------",filter_statuses)
        try:
            user_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            
            status_str = [s.value for s in filter_statuses] if filter_statuses else []
            orders = await self.order_repo.get_order_history(int(user_id), status_str)
            print("orders in 1 =======================",orders)
            return orders
        except Exception as e:
            logger.exception("failed in service get_order_history")
            raise e

    async def get_lender_orders(self, user_ctx) -> List:
        try:
            role_val = getattr(user_ctx, "role", None) if not isinstance(user_ctx, dict) else user_ctx.get("role")
            if Role:
                allowed = role_val in (Role.lender, "lender")
            else:
                allowed = role_val in ("lender",)
            if not allowed:
                raise RuntimeError("only lender can get orders")
            lender_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if lender_id is None or int(lender_id) <= 0:
                raise RuntimeError("invalid lender")
            orders = await self.order_repo.get_lender_orders(int(lender_id))
            return orders
        except Exception as e:
            logger.exception("failed in service get_lender_orders")
            raise e

    async def mark_order_as_returned(self, order_id: int, user_ctx) -> None:
        try:
            order = await self.order_repo.get_order_by_id(order_id)
            if order is None:
                raise RuntimeError("order not found")
            product_resp = await self.product_repo.find_by_id(order.product_id)
            if product_resp is None:
                raise RuntimeError("product not found")
            lender_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if int(product_resp.product.lender_id) != int(lender_id):
                raise RuntimeError("unauthorized lender")
            await self.order_repo.update_order_status(order_id, OrderStatus.Returned.value)
        except Exception as e:
            logger.exception("failed in service mark_order_as_returned")
            raise e

    async def get_all_approved_awaiting_orders(self, user_ctx) -> List:
        try:
            role_val = getattr(user_ctx, "role", None) if not isinstance(user_ctx, dict) else user_ctx.get("role")
            if Role:
                allowed = role_val in (Role.lender, "lender")
            else:
                allowed = role_val in ("lender",)
            if not allowed:
                raise RuntimeError("only lender can get returned awaiting orders")
            return_requests = await self.return_request_repo.get_all_return_requests(["approved"])
            orders = []
            for rr in return_requests:
                order = await self.order_repo.get_order_by_id(rr.order_id)
                if not order:
                    continue
                if order.status != OrderStatus.ReturnRequested:
                    continue
                orders.append(order)
            return orders
        except Exception as e:
            logger.exception("failed in service get_all_approved_awaiting_orders")
            raise e
