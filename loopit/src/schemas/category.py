from pydantic import BaseModel


class CategoryRequest(BaseModel):
    name: str
    price: float
    security: float


class CategoryResponse(BaseModel):
    id: int
    name: str
    price: float
    security: float
