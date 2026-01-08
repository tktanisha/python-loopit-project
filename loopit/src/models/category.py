from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class Category(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
         "json_encoders": {
            Decimal: float
        },
        
    }
    
    id: Optional[int] = Field(default=None, alias="ID")
    name: str = Field(alias="Name")
    price: Decimal = Field(alias="Price")
    security: Decimal = Field(alias="Security")

   
