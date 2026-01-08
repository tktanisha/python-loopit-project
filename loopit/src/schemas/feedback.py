
from pydantic import BaseModel, Field
from typing import Optional

class FeedbackRequest(BaseModel):
    order_id: Optional[int] = Field(default=None, gt=0)
    feedback_text: str = Field(min_length=1, max_length=1000)
    rating: Optional[int] = Field(default=None, ge=1, le=5)

class FeedbackSchema(BaseModel):
    id: int
    given_by: int
    given_to: int
    text: str
    rating: int
    created_at: str
