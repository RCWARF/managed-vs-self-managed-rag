import os
import boto3

REGION = os.environ.get("AWS_REGION", "us-west-2")

VECTOR_BUCKET = os.environ["VECTOR_BUCKET_NAME"]
VECTOR_INDEX = os.environ["VECTOR_INDEX_NAME"]

MODEL_ID = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "200"))
PUT_BATCH_SIZE = int(os.environ.get("PUT_BATCH_SIZE", "32"))

s3 = boto3.client("s3", region_name=REGION)
s3vectors = boto3.client("s3vectors", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)