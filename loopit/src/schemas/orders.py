

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from models.enums.order_status import OrderStatus
from schemas.product import ProductResponse
from models.orders import Order
from models.product import Product

class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    start_date: str
    end_date: str
    total_amount: float
    security_amount: float
    status: OrderStatus

class OrderSchema(BaseModel):
    id: int
    product_id: int
    user_id: int
    start_date: str
    end_date: str
    total_amount: float
    security_amount: float
    status: OrderStatus
    created_at: str
    image_url: Optional[str] = None

class OrderResponse(BaseModel):
    order: OrderSchema
    product: ProductResponse

def order_to_schema(o: Order) -> OrderSchema:
    return OrderSchema(
        id=o.id,
        product_id=o.product_id,
        user_id=o.user_id,
        start_date=o.start_date.isoformat(),
        end_date=o.end_date.isoformat(),
        total_amount=float(o.total_amount),
        security_amount=float(o.security_amount),
        status=o.status,
        created_at=o.created_at.isoformat(),
        image_url=None,
    )

def product_to_response(p) -> ProductResponse:
    product: Product = p.product  

    return ProductResponse(
        id=product.id,
        lender_id=product.lender_id,
        category_id=product.category_id,
        name=product.name,
        description=product.description,
        duration=product.duration,
        is_available=product.is_available,
        created_at=product.created_at.isoformat(),
        image_url=product.image_url,
    )
