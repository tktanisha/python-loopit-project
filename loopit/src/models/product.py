

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.category import Category
from models.user import User

class Product(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    lender_id: int = Field(alias="LenderID", gt=0)
    category_id: int = Field(alias="CategoryID", gt=0)
    name: str = Field(alias="Name", min_length=1, max_length=100)
    description: str = Field(alias="Description", min_length=1, max_length=500)
    duration: int = Field(alias="Duration", gt=0)
    is_available: bool = Field(default=True ,alias="IsAvailable")
    created_at: datetime = Field(default_factory=datetime.now, alias="CreatedAt")
    image_url: Optional[str] = Field(default=None, alias="ImageUrl")


class ProductFilter(BaseModel):
    category_id: Optional[str] = None
    lender_id: Optional[str] = None
    search: Optional[str] = None
    is_available: Optional[str] = None

class ProductResponse(BaseModel):
    product: Product
    category: Optional[Category] = None
    user: Optional[User] = None
