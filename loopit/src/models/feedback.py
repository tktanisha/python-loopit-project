
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Feedback(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    id: Optional[int] = Field(default=None, alias="ID")
    given_by: int = Field(alias="GivenBy", gt=0)
    given_to: int = Field(alias="GivenTo", gt=0)
    text: str = Field(alias="Text", min_length=1, max_length=1000)
    rating: int = Field(alias="Rating", ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.now, alias="CreatedAt")
