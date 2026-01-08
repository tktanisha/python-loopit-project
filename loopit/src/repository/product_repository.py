
import asyncio
import time
import logging
import botocore
from typing import Optional, List
from models.category import Category
from repository.category_repository import CategoryRepo
from repository.user.user_interface import UserRepo
from models.user import User
from helpers.app_settings import AppSettings
from models.product import Product,ProductFilter,ProductResponse 
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

logger = logging.getLogger(__name__)
settings = AppSettings()

class ProductRepo:
    def __init__(self, dynamodb, category_repo: CategoryRepo | None, user_repo:UserRepo |None):
        self.dynamodb = dynamodb
        self.table_name = settings.DDB_TABLE_NAME
        self.category_repo = category_repo
        self.user_repo = user_repo
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create(self, product: Product) -> None:
        pid = product.id if product.id is not None else time.time_ns()
        created_at = product.created_at.isoformat()
        base = {
            "ID": int(pid),
            "LenderID": int(product.lender_id),
            "CategoryID": int(product.category_id),
            "Name": product.name,
            "Description": product.description,
            "Duration": int(product.duration),
            "IsAvailable": bool(product.is_available),
            "ImageUrl": product.image_url or "",
            "CreatedAt": created_at,
        }
        items = [
            {**base, "pk": "PRODUCT", "sk": f"PRODUCT#{pid}"},
            {**base, "pk": "PRODUCT", "sk": f"LENDER#{product.lender_id}#ID#{pid}"},
            {**base, "pk": "PRODUCT", "sk": f"NAME#{product.name.lower()}#ID#{pid}"},
            {**base, "pk": f"CATEGORY#{product.category_id}", "sk": f"PRODUCT#{pid}"},
        ]
        transact_items = [{"Put": {"TableName": self.table_name, "Item": self.serializer.serialize(i)["M"]}} for i in items]
        try:
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=transact_items)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create product items")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while creating product items")
            raise RuntimeError(e)

    async def find_by_id(self, id: int) -> Optional[ProductResponse]:
        key = {"pk": {"S": "PRODUCT"}, "sk": {"S": f"PRODUCT#{id}"}}
        try:
            response = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to get product")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while getting product")
            raise RuntimeError(e)
        item = response.get("Item")
        if not item:
            return None
        doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
        lender_id = int(doc.get("LenderID")) if not isinstance(doc.get("LenderID"), int) else doc.get("LenderID")
        category_id = int(doc.get("CategoryID")) if not isinstance(doc.get("CategoryID"), int) else doc.get("CategoryID")
        product = Product.model_validate(
            {
                "ID": int(doc.get("ID")),
                "LenderID": lender_id,
                "CategoryID": category_id,
                "Name": doc.get("Name"),
                "Description": doc.get("Description"),
                "Duration": int(doc.get("Duration")),
                "IsAvailable": bool(doc.get("IsAvailable")),
                "CreatedAt": doc.get("CreatedAt"),
                "ImageUrl": doc.get("ImageUrl"),
            }
        )
        category = None
        if self.category_repo:
            try:
                category = await self.category_repo.find_by_id(category_id)
            except Exception:
                category = None
        user = None
        if self.user_repo:
            try:
                user = await self.user_repo.find_by_id(lender_id)
            except Exception:
                user = None
        return ProductResponse(product=product, category=category, user=user)

    async def find_all(self, filters: ProductFilter) -> List[ProductResponse]:
        if filters.category_id:
            pk = f"CATEGORY#{filters.category_id}"
            sk_prefix = "PRODUCT#"
        else:
            pk = "PRODUCT"
            if filters.lender_id:
                sk_prefix = f"LENDER#{filters.lender_id}"
            elif filters.search:
                sk_prefix = f"NAME#{filters.search.lower()}"
            else:
                sk_prefix = "PRODUCT#"
        try:
            response = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk AND begins_with(sk, :skPrefix)",
                ExpressionAttributeValues={":pk": {"S": pk}, ":skPrefix": {"S": sk_prefix}},
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query products")
            raise RuntimeError(e)
        
        except Exception as e:
            logger.exception("unexpected error while querying products")
            raise RuntimeError(e)
        
        items = response.get("Items", [])
        responses: List[ProductResponse] = []

        for item in items:
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            
            #if lender cand category id is not number in ddb than coerce it  into int
            Lender_id = int(doc.get("LenderID")) if not isinstance(doc.get("LenderID"), int) else doc.get("LenderID")
            Category_id = int(doc.get("CategoryID")) if not isinstance(doc.get("CategoryID"), int) else doc.get("CategoryID")
           

            product = Product.model_validate(
                {
                    "ID": int(doc.get("ID")),
                    "LenderID": int(doc.get("LenderID")),
                    "CategoryID": int(doc.get("CategoryID")),
                    "Name": doc.get("Name"),
                    "Description": doc.get("Description"),
                    "Duration": int(doc.get("Duration")),
                    "IsAvailable": bool(doc.get("IsAvailable")),
                    "CreatedAt": doc.get("CreatedAt"),
                    "ImageUrl": doc.get("ImageUrl"),
                }
            )
            

            if self.category_repo:
                try:
                    category = await self.category_repo.find_by_id(Category_id)
                except Exception as e:
                    raise RuntimeError(e)
                
            user = Optional[User]

            if self.user_repo:
                try:
                    user = await self.user_repo.find_by_id(Lender_id)
                    print("user=",user)
                except Exception as e:
                    raise RuntimeError(e)
                
            responses.append(ProductResponse(product= product, category= category, user= user))

        if filters.search:
            s = filters.search.lower()
            return [p for p in responses if (p.product.name and s in p.product.name.lower()) or (p.product.description and s in p.product.description.lower())]
        
        return responses

    async def update(self, product: Product) -> None:
        existing = await self.find_by_id(int(product.id))
        if not existing:
            raise RuntimeError("failed to fetch existing product")
        deletes = []
        if int(existing.product.category_id) != int(product.category_id):
            deletes.append(
                {
                    "Delete": {
                        "TableName": self.table_name,
                        "Key": {"pk": {"S": f"CATEGORY#{int(existing.product.category_id)}"}, "sk": {"S": f"PRODUCT#{int(product.id)}"}},
                    }
                }
            )
        if existing.product.name.casefold() != product.name.casefold():
            deletes.append(
                {
                    "Delete": {
                        "TableName": self.table_name,
                        "Key": {"pk": {"S": "PRODUCT"}, "sk": {"S": f"NAME#{existing.product.name.lower()}#ID#{int(product.id)}"}},
                    }
                }
            )
        update_expr = "SET #n = :name, Description = :description, #dur = :duration, IsAvailable = :isAvailable, CategoryID = :categoryId, LenderID = :lenderId"
        expr_attr_names = {"#n": "Name", "#dur": "Duration"}
        expr_attr_values = {
            ":name": {"S": product.name},
            ":description": {"S": product.description},
            ":duration": {"N": str(int(product.duration))},
            ":isAvailable": {"BOOL": bool(product.is_available)},
            ":categoryId": {"N": str(int(product.category_id))},
            ":lenderId": {"N": str(int(product.lender_id))},
        }
        keys = [
            {"pk": {"S": "PRODUCT"}, "sk": {"S": f"PRODUCT#{int(product.id)}"}},
            {"pk": {"S": "PRODUCT"}, "sk": {"S": f"LENDER#{int(product.lender_id)}#ID#{int(product.id)}"}},
            {"pk": {"S": "PRODUCT"}, "sk": {"S": f"NAME#{product.name.lower()}#ID#{int(product.id)}"}},
            {"pk": {"S": f"CATEGORY#{int(product.category_id)}"}, "sk": {"S": f"PRODUCT#{int(product.id)}"}},
        ]
        updates = [
            {
                "Update": {
                    "TableName": self.table_name,
                    "Key": k,
                    "UpdateExpression": update_expr,
                    "ExpressionAttributeNames": expr_attr_names,
                    "ExpressionAttributeValues": expr_attr_values,
                }
            }
            for k in keys
        ]
        transact_items = deletes + updates
        try:
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=transact_items)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update product records")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while updating product records")
            raise RuntimeError(e)

    async def delete(self, id: int) -> None:
        key = {"pk": {"S": "PRODUCT"}, "sk": {"S": f"PRODUCT#{int(id)}"}}
        try:
            response = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to fetch product")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while fetching product")
            raise RuntimeError(e)
        item = response.get("Item")
        if not item:
            raise RuntimeError("product not found")
        doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
        name = str(doc.get("Name"))
        lender_id = int(doc.get("LenderID")) if not isinstance(doc.get("LenderID"), int) else doc.get("LenderID")
        category_id = int(doc.get("CategoryID")) if not isinstance(doc.get("CategoryID"), int) else doc.get("CategoryID")
        deletes = [
            {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": "PRODUCT"}, "sk": {"S": f"PRODUCT#{int(id)}"}}}},
            {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": "PRODUCT"}, "sk": {"S": f"LENDER#{int(lender_id)}#ID#{int(id)}"}}}},
            {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": "PRODUCT"}, "sk": {"S": f"NAME#{name.lower()}#ID#{int(id)}"}}}},
            {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": f"CATEGORY#{int(category_id)}"}, "sk": {"S": f"PRODUCT#{int(id)}"}}}},
        ]
        try:
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=deletes)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to delete product records")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while deleting product records")
            raise RuntimeError(e)
