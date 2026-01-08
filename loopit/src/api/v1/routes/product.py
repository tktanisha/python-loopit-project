
from fastapi import APIRouter, Depends, status, Request
from helpers.auth_helper import AuthHelper
from service.product_service import ProductService
from schemas.product import ProductRequest
from setup.product_dependencies import get_product_service
from controller import product_controller as controller
from helpers.api_paths import ApiPaths



router = APIRouter(dependencies=[Depends(AuthHelper.verify_jwt)])

@router.get(ApiPaths.GET_PRODUCTS, status_code=status.HTTP_200_OK)
async def get_all_products(request: Request, product_service: ProductService = Depends(get_product_service)):
    return await controller.get_all_products(
        search=request.query_params.get("search"),
        lender_id=request.query_params.get("lender_id"),
        category_id=request.query_params.get("category_id"),
        is_available=request.query_params.get("is_available"),
        product_service=product_service,
    )

@router.get(ApiPaths.GET_PRODUCT_BY_ID, status_code=status.HTTP_200_OK)
async def get_product_by_id(id: int, product_service: ProductService = Depends(get_product_service)):
    return await controller.get_product_by_id(
        id=id,
        product_service=product_service,
    )

@router.post(ApiPaths.CREATE_PRODUCT, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductRequest, request:Request,product_service: ProductService = Depends(get_product_service)):
    user_ctx = request.state.user
    return await controller.create_product(
        product = product,
        product_service = product_service,
        user_ctx = user_ctx,
    )

@router.put(ApiPaths.UPDATE_PRODUCT, status_code=status.HTTP_200_OK)
async def update_product(id: int, product: ProductRequest,request:Request, product_service: ProductService = Depends(get_product_service)):
    user_ctx = request.state.user
    return await controller.update_product(
        id=id,
        product=product,
        product_service=product_service,
        user_ctx=user_ctx,
    )

@router.delete(ApiPaths.DELETE_PRODUCT, status_code=status.HTTP_200_OK)
async def delete_product(id: int,request:Request, product_service: ProductService = Depends(get_product_service)):
    user_ctx = request.state.user
    return await controller.delete_product(
        id=id,
        product_service=product_service,
        user_ctx=user_ctx,
    )
