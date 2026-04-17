import json
import time
import random

from .config import (
    bedrock,
    MODEL_ID

)


def get_embedding(text: str, max_retries=6):
    # NOTE: this truncates per-chunk text to 8000 chars for embedding input safety
    body = json.dumps({"inputText": text[:8000]})
    attempts = 0

    while True:
        t0 = time.perf_counter()
        try:
            response = bedrock.invoke_model(modelId=MODEL_ID, body=body)
            embedding = json.loads(response["body"].read())["embedding"]
            embed_ms = (time.perf_counter() - t0) * 1000.0
            return embedding, embed_ms, attempts

        except Exception:
            attempts += 1
            if attempts > max_retries:
                raise

            # Exponential backoff + jitter
            backoff = min(2 ** attempts, 10) * 0.2
            jitter = random.random() * 0.2
            time.sleep(backoff + jitter)