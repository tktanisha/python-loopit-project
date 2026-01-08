
import logging
from datetime import datetime
from repository.user.user_interface import UserRepo 
from repository.product_repository import ProductRepo
from schemas.product import ProductRequest, ProductResponse
from models.product import Product,ProductFilter
from models.enums.user import Role
from typing import Optional

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, product_repo: ProductRepo , user_repo:UserRepo):
        self.product_repo = product_repo
        self.user_repo = user_repo

    async def get_all_products(self, search: Optional[str], lender_id: Optional[str], category_id: Optional[str], is_available: Optional[str]):
        try:
            filters : ProductFilter = ProductFilter(
                category_id= category_id,
                search= search,
                is_available= is_available,
                lender_id= lender_id
            )
            products = await self.product_repo.find_all(filters)
            print("products=",products)
            return products
        
        except Exception as e:
            logger.exception("failed in service get_all_products")
            raise e

    async def get_product_by_id(self, id: int) -> ProductResponse | None:
        try:
            if id <= 0:
                raise RuntimeError("product ID must be a positive integer")
            product = await self.product_repo.find_by_id(id)
            if product is None:
                raise RuntimeError("product not found")
            return product
        
        except Exception as e:
            logger.exception("failed in service get_product_by_id")
            raise e

    async def create_product(self, product: ProductRequest, user_ctx) -> None:
        try:
            if user_ctx is None:
                raise RuntimeError("user not logged in")
            role_val = getattr(user_ctx, "role", None)
            if role_val not in (Role.lender, "lender"):
                raise RuntimeError("only lenders can create products")
            lender_id = getattr(user_ctx, "user_id", None) 
            if lender_id is None or int(lender_id) <= 0:
                raise RuntimeError("invalid lender")
            
            product: Product = Product(
                lender_id=int(lender_id),
                category_id=product.category_id,
                name=product.name,
                description=product.description,
                duration=product.duration,
                is_available=True,
                image_url=product.image_url,
                created_at=datetime.now(),
            )
            await self.product_repo.create(product)
        except Exception as e:
            logger.exception("failed in service create_product")
            raise e

    async def update_product(self, id: int, name: str, description: str, category_id: int, duration: int, is_available: bool, image_url: str | None, user_ctx) -> None:
        try:
            if user_ctx is None:
                raise RuntimeError("user not logged in")
            role_val = user_ctx.get("role", None)
            print("role=",role_val)
            if role_val not in (Role.lender, "lender"):
                raise RuntimeError("only lenders can update products")
            product_resp = await self.product_repo.find_by_id(id)
            if product_resp is None:
                raise RuntimeError("product not found")
            lender_id = user_ctx.get( "user_id", None) 
            if int(product_resp.product.lender_id) != int(lender_id):
                raise RuntimeError("you can only update your own products")
            
            product_resp.product.name = name
            product_resp.product.description = description
            product_resp.product.category_id = category_id
            product_resp.product.duration = duration
            product_resp.product.is_available = is_available
            product_resp.product.image_url = image_url

            await self.product_repo.update(product_resp.product)

        except Exception as e:
            logger.exception("failed in service update_product")
            raise e

    async def delete_product(self, id: int, user_ctx) -> None:
        try:
            if user_ctx is None:
                raise RuntimeError("user not logged in")
            role_val = user_ctx.get( "role", None)
            
            product_resp = await self.product_repo.find_by_id(id)

            if product_resp is None:
                raise RuntimeError("product not found")
            
            lender_id = user_ctx.get( "user_id", None)

            if int(product_resp.product.lender_id) != int(lender_id):
                raise RuntimeError("you can only delete your own products")
            
            await self.product_repo.delete(id)

        except Exception as e:
            logger.exception("failed in service delete_product")
            raise e
