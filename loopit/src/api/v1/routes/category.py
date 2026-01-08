from fastapi import Depends,APIRouter,status
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
from schemas.category import CategoryRequest,CategoryResponse
import controller.category_controller as controller
from service.category_service import CategoryService
from setup.category_dependency import get_category_service


router = APIRouter( dependencies= [Depends(AuthHelper.verify_jwt)])


@router.post(ApiPaths.CREATE_CATEGORY, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryRequest, category_service: CategoryService = Depends(get_category_service)):
    return await controller.create_category(
        category = category,
        category_service = category_service
    )


@router.get(ApiPaths.GET_CATEGORY, status_code=status.HTTP_200_OK)
async def get_all_category(category_service: CategoryService = Depends(get_category_service)):
    return await controller.get_all_category(
        category_service = category_service
    )


@router.put(ApiPaths.UPDATE_CATEGORY, status_code=status.HTTP_200_OK)
async def update_category(id, category:CategoryRequest, category_service: CategoryService = Depends(get_category_service)):
    return await controller.update_category(
        id = id,
        category = category,
        category_service = category_service
    )


@router.delete(ApiPaths.DELETE_CATEGORY, status_code=status.HTTP_200_OK)
async def delete_category(id, category_service: CategoryService = Depends(get_category_service)):
    return await controller.delete_category(
        id = id,
        category_service = category_service
    )


