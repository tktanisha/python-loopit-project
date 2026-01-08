
import asyncio
import time
import logging
import botocore
from datetime import datetime,timezone
from typing import List, Optional
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from models.return_request import ReturnRequest
from models.enums.return_req_status import ReturnStatus
from helpers.app_settings import AppSettings



logger = logging.getLogger(__name__)
settings = AppSettings()

class ReturnRequestRepo:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = settings.DDB_TABLE_NAME
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create_return_request(self, req: ReturnRequest) -> None:
        try:
            rid = req.id if req.id else time.time_ns()
            created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            item = {
                "pk": "RETURNREQUEST",
                "sk": f"ID#{rid}",
                "ID": int(rid),
                "OrderID": int(req.order_id),
                "RequestedBy": int(req.requested_by),
                "Status": req.status.value,
                "CreatedAt": created_at,
            }
            serialized_item = self.serializer.serialize(item)["M"]
            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=serialized_item,
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create return request")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while creating return request")
            raise RuntimeError(e)

    async def update_return_request_status(self, req_id: int, new_status: str) -> None:
        try:
            key = {"pk": {"S": "RETURNREQUEST"}, "sk": {"S": f"ID#{req_id}"}}
            await asyncio.to_thread(
                self.dynamodb.update_item,
                TableName=self.table_name,
                Key=key,
                UpdateExpression="SET #s = :status",
                ExpressionAttributeNames={"#s": "Status"},
                ExpressionAttributeValues={":status": {"S": new_status}},
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update return request status")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while updating return request status")
            raise RuntimeError(e)

    async def get_all_return_requests(self, filter_statuses: Optional[List[str]]) -> List[ReturnRequest]:
        try:
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": {"S": "RETURNREQUEST"}},
            )
            items = resp.get("Items", [])
            requests: List[ReturnRequest] = []
            status_map = {s for s in filter_statuses} if filter_statuses else set()
            for item in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                status_val = str(doc.get("Status"))
                if filter_statuses and status_val not in status_map:
                    continue
                rr = ReturnRequest.model_validate({
                    "ID": int(doc.get("ID")),
                    "OrderID": int(doc.get("OrderID")),
                    "RequestedBy": int(doc.get("RequestedBy")),
                    "Status": status_val,
                    "CreatedAt": doc.get("CreatedAt"),
                })
                requests.append(rr)
            return requests
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query return requests")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying return requests")
            raise RuntimeError(e)

    async def get_return_request_by_id(self, req_id: int) -> Optional[ReturnRequest]:
        try:
            key = {"pk": {"S": "RETURNREQUEST"}, "sk": {"S": f"ID#{req_id}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                return None
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            return ReturnRequest.model_validate({
                "ID": int(doc.get("ID")),
                "OrderID": int(doc.get("OrderID")),
                "RequestedBy": int(doc.get("RequestedBy")),
                "Status": str(doc.get("Status")),
                "CreatedAt": doc.get("CreatedAt"),
            })
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to get return request by id")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while getting return request by id")
            raise RuntimeError(e)

    async def save(self) -> None:
        return
