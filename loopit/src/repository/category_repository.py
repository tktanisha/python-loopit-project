from loopit.src.helpers.app_settings import AppSettings
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer
from loopit.src.models.category import Category
import botocore.exceptions
from typing import List,Optional
import time
import asyncio
import logging


logger=logging.getLogger(__name__)
settings= AppSettings()

class CategoryRepo:
    def __init__(self,dynamodb):
        self.table_name = settings.DDB_TABLE_NAME
        self.dynamodb = dynamodb
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()

    async def create_category(self,category: Category)-> None :
        try:
            category.id = int(time.time_ns())
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            item ={
                "pk":"CATEGORY",
                "sk":f"ID#{category.id}",
                **category.model_dump(by_alias=True),
                "CreatedAt":created_at
            }
            print("before db item=",item)

            item_db = self.serializer.serialize(item)["M"]
            print("item=",item_db)

            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=item_db,
            )
        
        except Exception as e:
            logger.exception("failed to create the category")
            raise RuntimeError(e)



    async def get_all_categories(self) -> List[Category]:
        try:
            response = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={
                    ":pk": {"S": "CATEGORY"},
                },
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query the ddb")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying categories")
            raise RuntimeError(e)

        items = response.get("Items", [])
        categories: List[Category] = []

        for item in items:
            try:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}

                cat_data = {
                    "ID": doc.get("ID"),
                    "Name": doc.get("Name"),
                    "Price": doc.get("Price"),
                    "Security": doc.get("Security"),
                }

                category_model = Category.model_validate(cat_data)
                categories.append(category_model)

            except Exception as e:
                logger.exception("failed to deserialize a category item")
                raise RuntimeError(e) 
       
        return categories
    

    async def find_by_id(self,id: int)-> Optional[Category]:
        print("catgery id===",id)
        try:
            response = await asyncio.to_thread(
                self.dynamodb.get_item,
                TableName= self.table_name,
                Key = {
                    "pk":{"S": "CATEGORY"},
                    "sk":{"S": f"ID#{id}"},
                },
            )
            print("response=",response)

        except botocore.exceptions.ClientError as e:
            logger.exception("aied to get the category")
            raise RuntimeError(e)
        
        except Exception as e:
            logger.exception("failed to get category (unexpected)")
            raise RuntimeError(e) 

        item= response.get("Item")
        print("item=",item)
        if not item:
            return None

        try:
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            cat_data = {
                "ID": doc.get("ID"),
                "Name": doc.get("Name"),
                "Price": doc.get("Price"),
                "Security": doc.get("Security"),
            }
            return Category.model_validate(cat_data)
        
        except Exception as e:
            logger.exception("failed to unmarshal category")
            raise RuntimeError(e)
        

    async def update_category(self, category: Category) -> None:
        if category.id is None:
            raise RuntimeError("category id must not be None for update")

        try:
            data = {
                "pk": "CATEGORY",
                "sk": f"ID#{category.id}",
                **category.model_dump(by_alias=True),
                "UpdatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            print("data=",data)

            item = self.serializer.serialize(data)["M"]

            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=item,
                # ensure we only update existing items
                ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update category (ClientError)")
            raise RuntimeError("e")
        except Exception as e:
            logger.exception("failed to update category (unexpected)")
            raise RuntimeError(e)



    async def delete_category(self,id:int)->None:
        try:
            await asyncio.to_thread(
                self.dynamodb.delete_item,
                TableName=self.table_name,
                Key={
                    "pk": {"S": "CATEGORY"},
                    "sk": {"S": f"ID#{id}"},
                },
                ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to delete category ")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("failed to delete category ")
            raise RuntimeError(e)
