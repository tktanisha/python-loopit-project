
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from models.enums.order_status import OrderStatus

class Order(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat(), Decimal: float},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    product_id: int = Field(alias="ProductID", gt=0)
    user_id: int = Field(alias="UserID", gt=0)
    start_date: datetime = Field(alias="StartDate")
    end_date: datetime = Field(alias="EndDate")
    total_amount: Decimal = Field(alias="TotalAmount")
    security_amount: Decimal = Field(alias="SecurityAmount")
    status: OrderStatus = Field(alias="Status")
    created_at: datetime = Field(default_factory=datetime.now, alias="CreatedAt")
