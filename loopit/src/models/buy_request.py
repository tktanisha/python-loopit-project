
# models/buying_request.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.enums.buy_request import BuyRequestStatus

class BuyingRequest(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    product_id: int = Field(alias="ProductId", gt=0)
    requested_by: int = Field(alias="RequestedBy", gt=0)
    status: BuyRequestStatus = Field(alias="Status")
    created_at: datetime = Field(default_factory=datetime.now(), alias="CreatedAt")
