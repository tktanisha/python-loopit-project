
from pydantic import BaseModel, Field

class ReturnRequestPayload(BaseModel):
    order_id: int = Field(gt=0)

class ReturnRequestSchema(BaseModel):
    id: int
    order_id: int
    requested_by: int
    status: int
    created_at: str


class ReturnRequestStatusUpdate(BaseModel):
    status: str
