from controller.auth_controller import login_controller, signup_controller
from fastapi import APIRouter, status,Depends
from helpers.api_paths import ApiPaths
from schemas.auth import LoginRequest,RegisterRequest 
from service.auth.auth_interface import AuthService
from setup.dependencies import get_auth_service

router = APIRouter(tags=["Auth"])


@router.post(ApiPaths.AUTH_SIGNUP, status_code=status.HTTP_201_CREATED)
async def signup(payload: RegisterRequest , auth_service: AuthService = Depends(get_auth_service)):
    return await signup_controller(
        payload= payload,
        auth_service=auth_service
    )


@router.post(ApiPaths.AUTH_LOGIN, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await login_controller(
        email=payload.email,
        password=payload.password,
        auth_service= auth_service
    )
