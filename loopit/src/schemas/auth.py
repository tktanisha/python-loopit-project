
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    phone_number: str
    address: str | None = None
    society_id: int

