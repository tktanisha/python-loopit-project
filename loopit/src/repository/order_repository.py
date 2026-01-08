
import asyncio
import time
import logging
import botocore
from datetime import datetime,timezone
from typing import List, Optional
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from models.orders import Order
from models.enums.order_status import OrderStatus
from repository.product_repository import ProductRepo
from helpers.app_settings import AppSettings

logger = logging.getLogger(__name__)
settings = AppSettings()

class OrderRepo:
    def __init__(self, dynamodb, product_repo:ProductRepo):
        self.dynamodb = dynamodb
        self.table_name = settings.DDB_TABLE_NAME
        self.product_repo = product_repo
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create_order(self, order: Order) -> None:
        try:
            oid = order.id if order.id else time.time_ns()

            start_date = order.start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date = order.end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            product_resp = await self.product_repo.find_by_id(order.product_id)
            if product_resp is None:
                raise RuntimeError("failed to fetch product for lender info")
            lender_id = int(product_resp.product.lender_id)
            base = {
                "ID": int(oid),
                "ProductID": int(order.product_id),
                "UserID": int(order.user_id),
                "StartDate": start_date,
                "EndDate": end_date,
                "TotalAmount": Decimal(str(order.total_amount)),
                "SecurityAmount": Decimal(str(order.security_amount)),
                "Status": order.status.value,
                "CreatedAt": created_at,
            }
            items = [
                {**base, "pk": f"USER#{order.user_id}", "sk": f"ORDER#ID#{oid}"},
                {**base, "pk": f"LENDER#{lender_id}", "sk": f"ORDER#ID#{oid}"},
                {**base, "pk": "ORDER", "sk": f"ID#{oid}"},
            ]
            transact_items = [{"Put": {"TableName": self.table_name, "Item": self.serializer.serialize(i)["M"]}} for i in items]
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=transact_items)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create order")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while creating order")
            raise RuntimeError(e)

    async def update_order_status(self, order_id: int, new_status: str) -> None:
        try:
            order = await self.get_order_by_id(order_id)
            if order is None:
                raise RuntimeError("order not found")
            product_resp = await self.product_repo.find_by_id(order.product_id)
            if product_resp is None:
                raise RuntimeError("failed to fetch product for order")
            lender_id = int(product_resp.product.lender_id)
            keys = [
                {"pk": {"S": f"USER#{order.user_id}"}, "sk": {"S": f"ORDER#ID#{order_id}"}},
                {"pk": {"S": f"LENDER#{lender_id}"}, "sk": {"S": f"ORDER#ID#{order_id}"}},
                {"pk": {"S": "ORDER"}, "sk": {"S": f"ID#{order_id}"}},
            ]
            update_expr = "SET #s = :status"
            expr_attr_names = {"#s": "Status"}
            expr_attr_values = {":status": {"S": new_status}}
            transact_items = [
                {
                    "Update": {
                        "TableName": self.table_name,
                        "Key": key,
                        "UpdateExpression": update_expr,
                        "ExpressionAttributeNames": expr_attr_names,
                        "ExpressionAttributeValues": expr_attr_values,
                    }
                }
                for key in keys
            ]
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=transact_items)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to update order status")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while updating order status")
            raise RuntimeError(e)

    async def get_order_history(self, user_id: int, filter_statuses: List[str]) -> List[Order]:
        try:
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk AND begins_with(sk, :skPrefix)",
                ExpressionAttributeValues={":pk": {"S": f"USER#{user_id}"}, ":skPrefix": {"S": "ORDER#"}},
            )
            items = resp.get("Items", [])
            orders: List[Order] = []
            for item in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                status_val = str(doc.get("Status"))
                order = Order.model_validate({
                    "ID": int(doc.get("ID")),
                    "ProductID": int(doc.get("ProductID")),
                    "UserID": int(doc.get("UserID")),
                    "StartDate": doc.get("StartDate"),
                    "EndDate": doc.get("EndDate"),
                    "TotalAmount": Decimal(str(doc.get("TotalAmount"))),
                    "SecurityAmount": Decimal(str(doc.get("SecurityAmount"))),
                    "Status": status_val,
                    "CreatedAt": doc.get("CreatedAt"),
                })
                orders.append(order)
            if filter_statuses:
                status_map = {s for s in filter_statuses}
                orders = [o for o in orders if o.status.value in status_map]
            return orders
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query order history")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying order history")
            raise RuntimeError(e)

    async def get_lender_orders(self, lender_id: int) -> List[Order]:
        try:
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk AND begins_with(sk, :skPrefix)",
                ExpressionAttributeValues={":pk": {"S": f"LENDER#{lender_id}"}, ":skPrefix": {"S": "ORDER#"}},
            )
            items = resp.get("Items", [])
            orders: List[Order] = []
            for item in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                order = Order.model_validate({
                    "ID": int(doc.get("ID")),
                    "ProductID": int(doc.get("ProductID")),
                    "UserID": int(doc.get("UserID")),
                    "StartDate": doc.get("StartDate"),
                    "EndDate": doc.get("EndDate"),
                    "TotalAmount": float(doc.get("TotalAmount")),
                    "SecurityAmount": float(doc.get("SecurityAmount")),
                    "Status": str(doc.get("Status")),
                    "CreatedAt": doc.get("CreatedAt"),
                })
                orders.append(order)
            return orders
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query lender orders")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying lender orders")
            raise RuntimeError(e)

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        try:
            key = {"pk": {"S": "ORDER"}, "sk": {"S": f"ID#{order_id}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                return None
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            return Order.model_validate({
                "ID": int(doc.get("ID")),
                "ProductID": int(doc.get("ProductID")),
                "UserID": int(doc.get("UserID")),
                "StartDate": doc.get("StartDate"),
                "EndDate": doc.get("EndDate"),
                "TotalAmount": float(doc.get("TotalAmount")),
                "SecurityAmount": float(doc.get("SecurityAmount")),
                "Status": str(doc.get("Status")),
                "CreatedAt": doc.get("CreatedAt"),
            })
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to get order by id")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while getting order by id")
            raise RuntimeError(e)
