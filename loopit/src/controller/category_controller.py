from service.category_service import CategoryService
from models.category import Category
from schemas.category import CategoryRequest, CategoryResponse
from fastapi import HTTPException,status
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response

async def create_category(category: CategoryRequest, category_service :CategoryService):
    category_payload:Category = Category(**category.model_dump())
    try:
        await category_service.create_category(category_payload)
        print("in controller")
    except Exception as e:
        return write_error_response(
            status_code = status.HTTP_400_BAD_REQUEST,
            error = "failed to create the catgeory",
            details = str(e)
        ) 
    
    return write_success_response(
        status_code = status.HTTP_201_CREATED,
        message = "category created successfully"
    )

async def get_all_category(category_service :CategoryService):
    try:
        categories = await category_service.get_all_categories()
        print("catgeories=",categories)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Failed to fetch the categories",
            details=str(e)
        )
    return write_success_response(
        status_code=status.HTTP_200_OK,
        data= categories
    )    

async def update_category(id, category:CategoryRequest, category_service :CategoryService):
    try:
        await category_service.update_category(id,name= category.name, price=category.price, security= category.security)

    except Exception as e:
        return write_error_response(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="update failed",
            details=str(e)
        )
    
    return write_success_response(
        status_code=status.HTTP_205_RESET_CONTENT,
        message= "category updated successfully"
    ) 

async def delete_category(id, category_service :CategoryService):
    try:
        await category_service.delete_category(id)

    except Exception as e:
        return write_error_response(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="category deletion failed",
            details=str(e)
        )
    
    return write_success_response(
        status_code=status.HTTP_200_OK,
        message= "category deleted successfully"
    ) 
