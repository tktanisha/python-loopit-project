
from pydantic import BaseModel, Field
from typing import Optional
from schemas.product import ProductResponse

class BuyRequestPayload(BaseModel):
    product_id: int = Field(gt=0)

class BuyRequest(BaseModel):
    id: int
    product_id: int
    requested_by: int
    status: int
    created_at: str

class UpdateBuyerRequestStatus(BaseModel):
    status: str    

class BuyRequestResponse(BaseModel):
    buy_request: BuyRequest
    product: ProductResponse
