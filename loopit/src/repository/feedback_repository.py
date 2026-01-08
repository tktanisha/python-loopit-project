
import asyncio
import time
import logging
import botocore
from typing import List
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from models.feedback import Feedback
from helpers.app_settings import AppSettings

logger = logging.getLogger(__name__)
settings = AppSettings() 

class FeedbackRepo:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = settings.DDB_TABLE_NAME
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    async def create_feedback(self, feedback: Feedback) -> None:
        try:
            fid = feedback.id if feedback.id else time.time_ns()
            created_at = feedback.created_at.isoformat()
            item = {
                "pk": "FEEDBACK",
                "sk": f"FEEDBACK#{fid}",
                "ID": int(fid),
                "GivenBy": int(feedback.given_by),
                "GivenTo": int(feedback.given_to),
                "Text": feedback.text,
                "Rating": int(feedback.rating),
                "CreatedAt": created_at,
            }
            serialized_item = self.serializer.serialize(item)["M"]
            await asyncio.to_thread(
                self.dynamodb.put_item,
                TableName=self.table_name,
                Item=serialized_item,
            )
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to create feedback")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while creating feedback")
            raise RuntimeError(e)

    async def get_all_feedbacks(self) -> List[Feedback]:
        try:
            resp = await asyncio.to_thread(
                self.dynamodb.query,
                TableName=self.table_name,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": {"S": "FEEDBACK"}},
            )
            items = resp.get("Items", [])
            feedbacks: List[Feedback] = []
            for item in items:
                doc = {k: self.deserializer.deserialize(v) for k, v in item.items()}
                fb = Feedback.model_validate({
                    "ID": int(doc.get("ID")),
                    "GivenBy": int(doc.get("GivenBy")),
                    "GivenTo": int(doc.get("GivenTo")),
                    "Text": doc.get("Text"),
                    "Rating": int(doc.get("Rating")),
                    "CreatedAt": doc.get("CreatedAt"),
                })
                feedbacks.append(fb)
            return feedbacks
        except botocore.exceptions.ClientError as e:
            logger.exception("failed to query feedbacks")
            raise RuntimeError(e)
        except Exception as e:
            logger.exception("unexpected error while querying feedbacks")
            raise RuntimeError(e)

    async def save(self) -> None:
        return
