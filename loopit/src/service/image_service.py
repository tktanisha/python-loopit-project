import boto3
import json
from botocore.exceptions import ClientError

LAMBDA_NAME = "project-loopit-stack2-UploadImageFunction-dTmmt1J7eRZU" 
REGION = "ap-south-1"

lambda_client = boto3.client("lambda", region_name=REGION)



def upload_image_via_lambda(payload: dict) -> dict:
    try:
        api_gateway_simulated_event = {
        "body": json.dumps(payload),  # The Go code looks for event.Body
        "resource": "/images/upload",
        "httpMethod": "PUT"
    }
    
        response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(api_gateway_simulated_event),
    )
        response_payload = json.loads(
            response["Payload"].read().decode("utf-8")
        )

        if response_payload.get("statusCode") != 200:
            raise RuntimeError(response_payload.get("body"))

        return json.loads(response_payload["body"])

    except ClientError as e:
        raise RuntimeError(f"Lambda invocation failed: {str(e)}")
