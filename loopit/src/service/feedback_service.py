
# services/feedback_service.py
import logging
from datetime import datetime
from models.feedback import Feedback

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self, feedback_repo, product_repo, order_repo):
        self.feedback_repo = feedback_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    async def give_feedback(self, order_id: int, feedback_text: str, rating: int, user_ctx) -> None:
        try:
            user_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if user_id is None or int(user_id) <= 0:
                raise RuntimeError("invalid user")
            logger.info(f"User {int(user_id)} attempting to give feedback for order {int(order_id)}")
            order = await self.order_repo.get_order_by_id(order_id)
            if order is None:
                raise RuntimeError("order not found")
            product_resp = await self.product_repo.find_by_id(order.product_id)
            if product_resp is None:
                raise RuntimeError("product not found")
            given_to = int(product_resp.product.lender_id)
            if int(user_id) == given_to:
                raise RuntimeError("you cannot give feedback to yourself")
            feedback = Feedback(
                given_by=int(user_id),
                given_to=given_to,
                rating=int(rating),
                text=feedback_text,
                created_at=datetime.now(),
            )
            await self.feedback_repo.create_feedback(feedback)
        except Exception as e:
            logger.exception("failed in service give_feedback")
            raise e

    async def get_all_given_feedbacks(self, user_ctx):
        try:
            user_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if user_id is None or int(user_id) <= 0:
                raise RuntimeError("invalid user")
            feedbacks = await self.feedback_repo.get_all_feedbacks()
            return [f for f in feedbacks if int(f.given_by) == int(user_id)]
        except Exception as e:
            logger.exception("failed in service get_all_given_feedbacks")
            raise e

    async def get_all_received_feedbacks(self, user_ctx):
        try:
            user_id = getattr(user_ctx, "user_id", None) if not isinstance(user_ctx, dict) else user_ctx.get("user_id")
            if user_id is None or int(user_id) <= 0:
                raise RuntimeError("invalid user")
            feedbacks = await self.feedback_repo.get_all_feedbacks()
            return [f for f in feedbacks if int(f.given_to) == int(user_id)]
        except Exception as e:
            logger.exception("failed in service get_all_received_feedbacks")
            raise e
