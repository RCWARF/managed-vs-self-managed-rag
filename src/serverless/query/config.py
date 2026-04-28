import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    region: str
    vector_bucket: str
    vector_index: str
    embed_model_id: str
    query_model_id: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            region=os.environ.get("AWS_REGION", "us-west-2"),
            vector_bucket=os.environ["VECTOR_BUCKET_NAME"],
            vector_index=os.environ["VECTOR_INDEX_NAME"],
            embed_model_id=os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"),
            query_model_id=os.environ.get("QUERY_MODEL_ID", "us.amazon.nova-lite-v1:0"),
        )