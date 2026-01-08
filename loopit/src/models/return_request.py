
# models/return_request.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.enums.return_req_status import ReturnStatus

class ReturnRequest(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    order_id: int = Field(alias="OrderID", gt=0)
    requested_by: int = Field(alias="RequestedBy", gt=0)
    status: ReturnStatus = Field(alias="Status")
    created_at: datetime = Field(default_factory=datetime.now, alias="CreatedAt")
