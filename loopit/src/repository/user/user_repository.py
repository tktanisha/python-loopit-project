import time
import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from models.user import User
from models.enums.user import Role
import botocore.exceptions
from repository.user.user_interface import UserRepo
from helpers.app_settings import AppSettings
from boto3.dynamodb.types import TypeDeserializer
from exception.user import UserNotFoundError, UserRepositoryError , UserAlreadyExistsError


logger = logging.getLogger(__name__)
setting= AppSettings()

class UserDynamoRepo(UserRepo):


    def __init__(self,dynamodb):
        self.table_name = setting.DDB_TABLE_NAME

        if not self.table_name:
            raise RuntimeError("DDB_TABLE_NAME is not configured")

        self.dynamodb = dynamodb
        self.deserializer = TypeDeserializer()


    def find_by_email(self, email: str) -> User:
        print("email=",email)
        try:
            resp = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    "pk": {"S": "USER"},
                    "sk": {"S": f"EMAIL#{email}"}
                }
            )

            print("response in repo=",resp)
        except Exception as e:
            print("tablename=",self.table_name)
            print("DDB_TABLE_NAME =", AppSettings.DDB_TABLE_NAME)
            logger.exception("in repo=",e)
            raise UserRepositoryError("DynamoDB get_item failed") from e

        if "Item" not in resp:
            raise UserNotFoundError(f"user not found with email {email}")

        item = {k: self.deserializer.deserialize(v) for k, v in resp["Item"].items()}

        print("user item =",item)
        return User(
            id=int(item["ID"]),
            full_name=item["FullName"],
            email=item["Email"],
            phone_number=item["PhoneNumber"],
            address=item["Address"],
            password_hash=item["PasswordHash"],
            society_id=int(item["SocietyID"]),
            role=Role(item["Role"]),
            created_at=datetime.fromisoformat(
            item["CreatedAt"].replace("Z", "+00:00")
    ),
        )

    
    def create(self, user: User) -> None:
        user.id = int(time.time_ns())
        role = user.role.value
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        common_attrs = {
            "ID": {"N": str(user.id)},
            "FullName": {"S": user.full_name},
            "Email": {"S": user.email},
            "PhoneNumber": {"S": user.phone_number},
            "Address": {"S": user.address},
            "PasswordHash": {"S": user.password_hash},
            "SocietyID": {"N": str(user.society_id)},
            "Role": {"S": role},
            "CreatedAt": {"S": created_at},
        }

        transact_items = [
            {
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": "USER"},
                        "sk": {"S": f"ID#{user.id}"},
                        **common_attrs,
                    },
                    "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                }
            },
            {
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": "USER"},
                        "sk": {"S": f"EMAIL#{user.email}"},
                        **common_attrs,
                    },
                    "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                }
            },
            {
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": "USER"},
                        "sk": {"S": f"ROLE#{role}#USER#{user.id}"},
                        **common_attrs,
                    },
                    "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                }
            },
            {
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": f"SOCIETY#{user.society_id}"},
                        "sk": {"S": f"USER#ID#{user.id}"},
                        **common_attrs,
                    },
                    "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                }
            },
        ]

        try:
            self.dynamodb.transact_write_items(
                TransactItems=transact_items
            )

        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            code = e.response["Error"]["Code"]

            if code == "TransactionCanceledException":
                raise UserAlreadyExistsError("user already exists") from e

            raise UserRepositoryError("failed to create user") from e
        

    async def become_lender(self, user_id: int) -> None:
        try:
            key = {"pk": {"S": "USER"}, "sk": {"S": f"ID#{int(user_id)}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                raise RuntimeError("user not found")
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            old_role = str(doc.get("Role", "")).lower()
            name = str(doc.get("Name")) if doc.get("Name") is not None else ""
            society_id = int(doc.get("SocietyID")) if doc.get("SocietyID") not in (None, "") else None

            update = {
                "Update": {
                    "TableName": self.table_name,
                    "Key": key,
                    "UpdateExpression": "SET #r = :role",
                    "ExpressionAttributeNames": {"#r": "Role"},
                    "ExpressionAttributeValues": {":role": {"S": "lender"}},
                }
            }
            deletes = []
            if old_role:
                deletes.append({
                    "Delete": {
                        "TableName": self.table_name,
                        "Key": {"pk": {"S": "USER"}, "sk": {"S": f"ROLE#{old_role}#ID#{int(user_id)}"}},
                    }
                })
            puts = [{
                "Put": {
                    "TableName": self.table_name,
                    "Item": {
                        "pk": {"S": "USER"},
                        "sk": {"S": f"ROLE#lender#ID#{int(user_id)}"},
                        "Role": {"S": "lender"},
                        "ID": {"N": str(int(user_id))},
                    },
                }
            }]
            txn = deletes + [update] + puts
            await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=txn)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to become lender")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error in become_lender")
            raise RuntimeError(e)

    async def find_all(self, filters: dict) -> List[User]:
        try:
            search = (filters or {}).get("search") or ""
            role = (filters or {}).get("role") or ""
            society_id = (filters or {}).get("society_id") or ""
            if society_id:
                pk = f"SOCIETY#{society_id}"
                sk_prefix = "USER#"
            else:
                pk = "USER"
                if role:
                    sk_prefix = f"ROLE#{str(role).lower()}"
                elif search:
                    sk_prefix = f"NAME#{str(search).lower()}"
                else:
                    sk_prefix = "ID#"
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk AND begins_with(sk, :sk)",
                ExpressionAttributeValues={":pk": {"S": pk}, ":sk": {"S": sk_prefix}},
            )
            items = resp.get("Items", [])
            users: List[User] = []
            for it in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in it.items()}
                u = User.model_validate({
                    "ID": int(doc.get("ID")),
                    "FullName": doc.get("FullName"),
                    "Role": doc.get("Role"),
                    "PhoneNumber":doc.get("PhoneNumber"),
                    "Address":doc.get("Address"),
                    "PasswordHash":doc.get("PasswordHash"),
                    "SocietyID": int(doc.get("SocietyID")) if doc.get("SocietyID") not in (None, "") else None,
                    "Email": doc.get("Email"),
                    "CreatedAt": doc.get("CreatedAt"),
                })
                users.append(u)
            if search and not role and not society_id:
                s = str(search).lower()
                users = [u for u in users if u.name and s in u.name.lower()]
            return users
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to find all users")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error in find_all")
            raise RuntimeError(e)

    async def find_by_id(self, user_id: int) -> Optional[User]:
        print("userid=================",user_id)
        try:
            key = {
                "pk": {"S": "USER"},
                "sk": {"S": f"ID#{user_id}"}
                }
            response = await asyncio.to_thread(
                self.dynamodb.get_item,
                TableName=self.table_name, 
                Key=key
                )
            
            print("response======",response)
            item = response.get("Item")

            if not item:
                return None
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            print("doc==",doc)
            return User.model_validate({
                "ID": int(doc.get("ID")),
                "FullName": doc.get("FullName"),
                "Address": doc.get("Address"),
                "Role": doc.get("Role"),
                "PhoneNumber":doc.get("PhoneNumber"),
                "PasswordHash":doc.get("PasswordHash"),
                "SocietyID": int(doc.get("SocietyID")),
                "Email": doc.get("Email"),
                "CreatedAt": doc.get("CreatedAt"),
            })
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to find user by id")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error in find_by_id")
            raise RuntimeError(e)

    async def delete_by_id(self, user_id: int) -> None:
        try:
            key = {"pk": {"S": "USER"}, "sk": {"S": f"ID#{int(user_id)}"}}
            resp = await asyncio.to_thread(self.dynamodb.get_item, TableName=self.table_name, Key=key)
            item = resp.get("Item")
            if not item:
                return
            doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            role = str(doc.get("Role", "")).lower()
            name = str(doc.get("Name")) if doc.get("Name") is not None else ""
            society_id = int(doc.get("SocietyID")) if doc.get("SocietyID") not in (None, "") else None
            deletes = [
                {"Delete": {"TableName": self.table_name, "Key": key}},
                {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": "USER"}, "sk": {"S": f"ROLE#{role}#ID#{int(user_id)}"}}}} if role else None,
                {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": "USER"}, "sk": {"S": f"NAME#{name.lower()}#ID#{int(user_id)}"}}}} if name else None,
                {"Delete": {"TableName": self.table_name, "Key": {"pk": {"S": f"SOCIETY#{int(society_id)}"}, "sk": {"S": f"USER#{int(user_id)}"}}}} if society_id else None,
            ]
            deletes = [d for d in deletes if d is not None]
            if deletes:
                await asyncio.to_thread(self.dynamodb.transact_write_items, TransactItems=deletes)
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to delete user")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error in delete_by_id")
            raise RuntimeError(e)
