
from fastapi import status
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response
from service.product_service import ProductService
from schemas.product import ProductRequest
from typing import Optional
from models.enums.user import Role

async def get_all_products(search: Optional[str], lender_id: Optional[str], category_id: Optional[str], is_available: Optional[str], product_service: ProductService):
    try:
        products = await product_service.get_all_products(
            search=search,
            lender_id=lender_id,
            category_id=category_id,
            is_available=is_available,
        )
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch products",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=products if not hasattr(products, "model_dump") else [p.model_dump() for p in products],
    )

async def get_product_by_id(id: int, product_service: ProductService):
    try:
        product = await product_service.get_product_by_id(id)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error="product not found",
            details=str(e),
        )
    data = product.model_dump() if hasattr(product, "model_dump") else product
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=data,
    )

async def create_product(product: ProductRequest, product_service: ProductService, user_ctx):
    try:
        role_val= user_ctx.get("role",None)
        if role_val not in (Role.lender, "lender"):
            raise RuntimeError("only lenders can delete products")

        await product_service.create_product(product, user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="failed to create product",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="product created successfully",
    )

async def update_product(id: int, product: ProductRequest, product_service: ProductService, user_ctx):
    try:
        role_val= user_ctx.get("role",None)
        if role_val not in (Role.lender, "lender"):
            raise RuntimeError("only lenders can delete products")
        
        await product_service.update_product(
            id=id,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            duration=product.duration,
            is_available=product.is_available,
            image_url=product.image_url,
            user_ctx=user_ctx,
        )
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="failed to update product",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="product updated successfully",
    )

async def delete_product(id: int, product_service: ProductService, user_ctx):

    try:
        role_val= user_ctx.get("role",None)
        if role_val not in (Role.lender, "lender"):
            raise RuntimeError("only lenders can delete products")
    
        await product_service.delete_product(id, user_ctx)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            error="failed to delete product",
            details=str(e),
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="product deleted successfully",
    )
