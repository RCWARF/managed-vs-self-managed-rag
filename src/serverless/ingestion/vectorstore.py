import time

from .config import (
        s3vectors,
        VECTOR_BUCKET,
        VECTOR_INDEX
)
def put_vectors_batch(vectors):
        """
        vectors: list of {"key": str, "data": {"float32": [...]}, "metadata": {...}}
        """
        t0 = time.perf_counter()
        resp = s3vectors.put_vectors(
            vectorBucketName=VECTOR_BUCKET,
            indexName=VECTOR_INDEX,
            vectors=vectors
        )
        put_ms = (time.perf_counter() - t0) * 1000.0
        return resp, put_ms