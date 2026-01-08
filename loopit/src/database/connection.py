import boto3

dynamodb_client = boto3.client("dynamodb")


def get_dynamodb():
    return dynamodb_client
