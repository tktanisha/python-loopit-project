
import asyncio
import time
import logging
import botocore
from typing import Optional, List
from datetime import datetime,timezone
from helpers.app_settings import AppSettings
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from models.buy_request import BuyingRequest
from models.enums.buy_request import BuyRequestStatus

logger = logging.getLogger(__name__)
settings = AppSettings()

class BuyRequestRepo:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = settings.DDB_TABLE_NAME
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create_buyer_request(self, req: BuyingRequest) -> None:
        try:
            rid = req.id if req.id else time.time_ns()
            created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            base = {
                "ID": int(rid),
                "ProductId": int(req.product_id),
                "RequestedBy": int(req.requested_by),
                "Status": req.status.value,
                "CreatedAt": created_at,
            }
            items = [
                {**base, "pk": "BUYREQUEST", "sk": f"ID#{rid}"},
                {**base, "pk": "BUYREQUEST", "sk": f"STATUS#{req.status.value}#ID#{rid}"},
            ]
            transact_items = [{"Put": {"TableName": self.table_name, "Item": self.serializer.serialize(i)["M"]}} for i in items]
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=transact_items)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create buyer request")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while creating buyer request")
            raise RuntimeError(e)

    async def get_all_buyer_requests(self, product_id: Optional[int] = None, filter_statuses: Optional[List[str]]=None) -> List[BuyingRequest]:
        try:
            sk_prefix = f"STATUS#{filter_statuses[0]}" if filter_statuses else "ID#"
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk AND begins_with(sk, :skPrefix)",
                ExpressionAttributeValues={":pk": {"S": "BUYREQUEST"}, ":skPrefix": {"S": sk_prefix}},
            )
            items = resp.get("Items", [])
            requests: List[BuyingRequest] = []

            for item in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                status_val = str(doc.get("Status"))
                
                if product_id and int(doc.get("ProductId")) != int(product_id):
                    continue
                if filter_statuses and status_val != filter_statuses[0]:
                    continue
                req = BuyingRequest.model_validate({
                    "ID": int(doc.get("ID")),
                    "ProductId": int(doc.get("ProductId")),
                    "RequestedBy": int(doc.get("RequestedBy")),
                    "Status": status_val,
                    "CreatedAt": doc.get("CreatedAt"),
                })
                requests.append(req)
            return requests
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query buyer requests")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying buyer requests")
            raise RuntimeError(e)

    async def update_status_buyer_request(self, req_id: int, new_status: str) -> None:
        try:
            key = {"pk": {"S": "BUYREQUEST"}, "sk": {"S": f"ID#{req_id}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                raise RuntimeError("buyer request not found")
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            old_status = str(doc.get("Status"))
            update_expr = "SET #s = :status"
            expr_attr_names = {"#s": "Status"}
            expr_attr_values = {":status": {"S": new_status}}
            deletes = [{
                "Delete": {
                    "TableName": self.table_name,
                    "Key": {"pk": {"S": "BUYREQUEST"}, "sk": {"S": f"STATUS#{old_status}#ID#{req_id}"}},
                }
            }]
            update = {
                "Update": {
                    "TableName": self.table_name,
                    "Key": key,
                    "UpdateExpression": update_expr,
                    "ExpressionAttributeNames": expr_attr_names,
                    "ExpressionAttributeValues": expr_attr_values,
                }
            }
            put_new = {
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": "BUYREQUEST"},
                        "sk": {"S": f"STATUS#{new_status}#ID#{req_id}"},
                        "Status": {"S": new_status},
                        "ID": {"N": str(req_id)},
                    },
                }
            }
            txn = deletes + [update] + [put_new]
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=txn)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update buyer request status")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while updating buyer request status")
            raise RuntimeError(e)

    async def get_buyer_request_by_id(self, req_id: int) -> Optional[BuyingRequest]:
        try:
            key = {"pk": {"S": "BUYREQUEST"}, "sk": {"S": f"ID#{req_id}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                return None
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            return BuyingRequest.model_validate({
                "ID": int(doc.get("ID")),
                "ProductId": int(doc.get("ProductId")),
                "RequestedBy": int(doc.get("RequestedBy")),
                "Status": str(doc.get("Status")),
                "CreatedAt": doc.get("CreatedAt"),
            })
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to get buyer request by id")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while getting buyer request by id")
            raise RuntimeError(e)

    async def delete_buyer_request(self, req_id: int) -> None:
        try:
            key = {"pk": {"S": "BUYREQUEST"}, "sk": {"S": f"ID#{req_id}"}}
            await asyncio.to_thread(self.dynamodb.delete_item, TableName=self.table_name, Key=key)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to delete buyer request")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while deleting buyer request")
            raise RuntimeError(e)
