from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
from setup.user_dependencies import get_user_service
from service.user_service import UserService
from controller import user_controller as controller

router = APIRouter(dependencies=[Depends(AuthHelper.verify_jwt)])

@router.patch(ApiPaths.BECOME_LENDER, status_code=status.HTTP_200_OK)
async def become_lender(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user_ctx = request.state.user
    return await controller.become_lender(
        user_service=user_service,
        user_ctx=user_ctx,
    )

@router.get(ApiPaths.GET_USERS, status_code=status.HTTP_200_OK)
async def get_all_users(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user_ctx = request.state.user
    search = request.query_params.get("search")
    role = request.query_params.get("role")
    society_id = request.query_params.get("society_id")

    return await controller.get_all_users(
        search=search,
        role=role,
        society_id=society_id,
        user_service=user_service,
        user_ctx=user_ctx,
    )

@router.get(ApiPaths.GET_USER_BY_ID, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id: int,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user_ctx = request.state.user
    return await controller.get_user_by_id(
        id=id,
        user_service=user_service,
        user_ctx=user_ctx,
    )

@router.delete(ApiPaths.DELETE_USER_BY_ID, status_code=status.HTTP_200_OK)
async def delete_user_by_id(
    id: int,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    user_ctx = request.state.user
    return await controller.delete_user_by_id(
        id=id,
        user_service=user_service,
        user_ctx=user_ctx,
    )
