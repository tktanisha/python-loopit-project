from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from models.enums.user import Role


class User(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
      
    id: int | None = Field(default=None, alias="ID")
    full_name: str = Field(alias="FullName")
    email: EmailStr = Field(alias="Email")
    phone_number: str = Field(alias="PhoneNumber")
    address: str = Field(alias="Address")
    password_hash: str = Field(alias="PasswordHash")
    society_id: int = Field(alias="SocietyID")
    role: Role = Field(default=Role.user, alias="Role")
    created_at: datetime = Field(default_factory=datetime.now(), alias="CreatedAt")

    

class UserContext(BaseModel):
    user_id: int
    role: str
