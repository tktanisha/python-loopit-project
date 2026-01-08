
from helpers.app_settings import AppSettings
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from models.society import Society  
import botocore.exceptions
from typing import List, Optional
import time
import asyncio
import logging

logger = logging.getLogger(__name__)
settings = AppSettings()


class SocietyRepo:
    def __init__(self, dynamodb):
        self.table_name = settings.DDB_TABLE_NAME
        self.dynamodb = dynamodb 
        self.deserializer = TypeDeserializer()
        self.serializer = TypeSerializer()

    async def create(self, society: Society) -> None:
        try:
            society.id = int(time.time_ns())
            created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            item = {
                "pk": "SOCIETY",
                "sk": f"ID#{society.id}",
                **society.model_dump(by_alias=True), 
                "CreatedAt": created_at,
            }

            item_db = self.serializer.serialize(item)["M"]

            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=item_db,
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create society (ClientError)")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("failed to create society (unexpected)")
            raise RuntimeError(e)

    async def find_all(self) -> List[Society]:
        try:
            response = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={
                    ":pk": {"S": "SOCIETY"},
                },
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query societies (ClientError)")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("failed to query societies (unexpected)")
            raise RuntimeError(e)

        items = response.get("Items", [])
        societies: List[Society] = []

        for item in items:
            try:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                soc_data = {
                    "ID": doc.get("ID"),
                    "Name": doc.get("Name"),
                    "Location": doc.get("Location"),
                    "Pincode": doc.get("Pincode"),
                    "CreatedAt": doc.get("CreatedAt"),
                }
                society_model = Society.model_validate(soc_data)
                societies.append(society_model)
            except Exception as e:
                logger.exception("failed to deserialize a society item")
                raise RuntimeError(e)

        return societies

   
    async def find_by_id(self, id: int) -> Optional[Society]:
        try:
            resp = await asyncio.to_thread(
                self.dynamodb.get_item,
                TableName=self.table_name,
                Key={
                    "pk": {"S": "SOCIETY"},
                    "sk": {"S": f"ID#{id}"},
                },
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to get society (ClientError)")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("failed to get society (unexpected)")
            raise RuntimeError(e)

        item = resp.get("Item")
        if not item:
            return None

        try:
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            soc_data = {
                "ID": doc.get("ID"),
                "Name": doc.get("Name"),
                "Location": doc.get("Location"),
                "Pincode": doc.get("Pincode"),
                "CreatedAt": doc.get("CreatedAt"),
            }
            return Society.model_validate(soc_data)
        except Exception as e:
            logger.exception("failed to unmarshal society")
            raise RuntimeError("failed to deserialize society") from e


    async def update(self, society: Society) -> None:
      
        if society.id is None:
            raise RuntimeError("society id must not be None for update")

        try:
            data = {
                "pk": "SOCIETY",
                "sk": f"ID#{society.id}",
                **society.model_dump(by_alias=True),
                "CreatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

            item = self.serializer.serialize(data)["M"]

            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=item,
                ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update society (ClientError)")
            raise RuntimeError( e)
        except Exception as e:
            logger.exception("failed to update society (unexpected)")
            raise RuntimeError(e)

    async def delete(self, id: int) -> None:
        try:
            await asyncio.to_thread(
                self.dynamodb.delete_item,
                TableName=self.table_name,
                Key={
                    "pk": {"S": "SOCIETY"},
                    "sk": {"S": f"ID#{id}"},
                },
                 ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to delete society (ClientError)")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("failed to delete society (unexpected)")
            raise RuntimeError(e)
