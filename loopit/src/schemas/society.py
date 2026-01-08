from pydantic import BaseModel

class SocietyResponse(BaseModel):
    id: int
    name: str
    location: str
    pincode: str


class SocietyRequest(BaseModel):
    name: str
    location: str
    pincode: str