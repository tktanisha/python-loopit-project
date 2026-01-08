
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductImage(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    product_id: int = Field(alias="ProductID", gt=0)
    image_url: str = Field(alias="ImageURL", min_length=1)
    uploaded_at: datetime = Field(default_factory=datetime.now, alias="UploadedAt")
