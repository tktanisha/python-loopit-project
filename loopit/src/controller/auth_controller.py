from fastapi import HTTPException, status
from service.auth.auth_interface import AuthService
from schemas.auth import RegisterRequest
from models.user import User
from exception.user import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    AuthServiceError,
)
import logging


logger= logging.getLogger(__name__)


async def signup_controller(
    payload: RegisterRequest,
    auth_service: AuthService,
):
   
    user = User(
        full_name=payload.fullname,
        email=payload.email,
        phone_number=payload.phone_number,
        address=payload.address or "",
        password_hash=payload.password,  # raw password for now
        society_id=payload.society_id,
    )
    try:
        await auth_service.register(user = user)

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )

    try:
        token,user_db = await auth_service.login(user.email,payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return {
        "token":token,
        "user":{
            "id": user_db.id,
            "name": user_db.full_name,
            "role": user_db.role.value,
        }
    }         



async def login_controller(
    email: str,
    password: str,
    auth_service: AuthService,
):
    try:
        token, user = await auth_service.login(email, password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.full_name,
            "role": user.role.value,
        },
    }
