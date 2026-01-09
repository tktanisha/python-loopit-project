
from fastapi import Depends,APIRouter,status
from helpers.auth_helper import AuthHelper
from helpers.api_paths import ApiPaths
import controller.society_controller as controller
from service.category_service import CategoryService
from schemas.society import SocietyRequest,SocietyResponse
from setup.society_dependency import get_society_service
from helpers.auth_helper import AuthHelper


router = APIRouter( dependencies= [Depends(AuthHelper.verify_jwt)] )

@router.post(ApiPaths.CREATE_SOCIETY , status_code=status.HTTP_201_CREATED)
async def create_society(society: SocietyRequest, society_service= Depends(get_society_service)):
    return await controller.create_society(
        society = society, 
        society_service = society_service
          )

@router.get(ApiPaths.GET_SOCIETY , status_code=status.HTTP_200_OK)
async def get_all_society(society_service= Depends(get_society_service)):
    return await controller.get_all_societies(
        society_service = society_service
    )

@router.put(ApiPaths.UPDATE_SOCIETY ,status_code = status.HTTP_200_OK)
async def update_society(id, society:SocietyRequest, society_service= Depends(get_society_service)):
    return await controller.update_society(
        id = id,
        society = society,
        society_service = society_service
    )

@router.delete(ApiPaths.DELETE_SOCIETY, status_code=status.HTTP_200_OK)
async def delete_society(id, society_service= Depends(get_society_service)):
    return await controller.delete_society(
        id = id,
        society_service = society_service
    )
