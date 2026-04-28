import boto3
from config import AppConfig


def create_bedrock_client(config: AppConfig):
    return boto3.client("bedrock-runtime", region_name=config.region)


def create_s3vectors_client(config: AppConfig):
    return boto3.client("s3vectors", region_name=config.region)