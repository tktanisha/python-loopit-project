from repository.category_repository import CategoryRepo
from models.category import Category
import logging
from decimal import Decimal


logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self,category_repo: CategoryRepo):
        self.category_repo = category_repo

    async def create_category(self, category: Category)->None:
        try:
             await self.category_repo.create_category(category= category)
        except Exception as e:
            logger.exception("failed in service in create category=")
            raise e

    async def get_all_categories(self):
        try:
            categories = await self.category_repo.get_all_categories()
        except Exception as e:
            logger.exception("failed in service in get all category=")
            raise e 
        return categories               
    

    async def update_category(self, id: int, name: str, price:float, security:float)-> None:
        try:
            category: Category | None = await self.category_repo.find_by_id(id)

        except Exception as e:
            raise e    
        
        if category is None:
                raise RuntimeError(f"catgeory of {id} do not exist ")
        
        
        category.name= name
        category.price= Decimal(str(price))
        category.security= Decimal(str(security))

        try:
            await self.category_repo.update_category(category)

        except Exception as e:
            logger.exception("failed in update category service")
            raise e    
        

    async def delete_category(self, id: int)->None:
        try:
            category: Category | None = await self.category_repo.find_by_id(id)

        except Exception as e:
            raise e    
        
        if category is None:
                raise RuntimeError(f"catgeory of {id} do not exist ")
        
        try:
            await self.category_repo.delete_category(id)
        except Exception as e:
            logger.exception("failed in service in delete category=")
            raise e 
             