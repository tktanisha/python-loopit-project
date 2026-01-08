
from pydantic import BaseModel, Field
from typing import Optional

class ProductRequest(BaseModel):
    lender_id: Optional[int] = None #none is here default value
    category_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    duration: int = Field(gt=0)
    is_available: Optional[bool] = True
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    lender_id: int
    category_id: int
    name: str
    description: str
    duration: int
    is_available: bool
    created_at: str
    image_url: Optional[str] = None
