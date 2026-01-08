from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Society(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    id:Optional[int] = Field(default=None, alias="ID")
    name: str = Field(alias="Name")
    location: str = Field(alias="Location")
    pincode: str = Field(alias="Pincode")
    created_at: datetime = Field(default_factory=datetime.now(), alias="CreatedAt")

    
