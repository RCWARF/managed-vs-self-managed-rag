import time
import hashlib
from statistics import mean

from .chunking import chunk_text
from .embedder import get_embedding
from .vectorstore import put_vectors_batch
from .config import (
    s3,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PUT_BATCH_SIZE,
)

 # -------- Timing helpers --------
def pct(values, p):
    if not values:
        return None
    v = sorted(values)
    k = int(round((p / 100.0) * (len(v) - 1)))
    return v[k]

def process_one_message(msg_body: dict, stats: dict):
    bucket = msg_body["bucket"]
    key = msg_body["key"]
    etag = msg_body["etag"]

    file_t0 = time.perf_counter()

    # S3 read timing
    t0 = time.perf_counter()
    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read().decode("utf-8", errors="ignore")
    s3_read_ms = (time.perf_counter() - t0) * 1000.0

    # chunk timing
    t0 = time.perf_counter()
    chunks = chunk_text(content, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    chunking_ms = (time.perf_counter() - t0) * 1000.0

    embed_ms_list = []
    retries_total = 0
    chunks_with_retry = 0
    put_ms_list = []

    vectors_batch = []
    total_vectors_put = 0

    safe_key = hashlib.sha256(f"{bucket}/{key}/{etag}".encode("utf-8")).hexdigest()

    for idx, chunk in enumerate(chunks):
        embedding, embed_ms, attempts = get_embedding(chunk)
        embed_ms_list.append(embed_ms)
        retries_total += attempts
        if attempts > 0:
            chunks_with_retry += 1



        #If you expect keys to include odd chars, optionally hash the key portion:
        
        vector_key = f"{safe_key}|chunk:{idx:06d}"

        vectors_batch.append({
            "key": vector_key,
            "data": {"float32": embedding},
            # Metadata: store enough to reconstruct context later.
            # You *can* store the chunk text here (like your OpenSearch "content"),
            # but if metadata limits bite, store chunk text in S3 and keep a pointer only.
            "metadata": {
                "source_bucket": bucket,
                "source_key": key,
                "etag": etag,
                "chunk_index": idx,
                "ingested_at": int(time.time()),
                "content": chunk
            }
        })

        # Flush batches to S3 Vectors
        if len(vectors_batch) >= PUT_BATCH_SIZE:
            _, put_ms = put_vectors_batch(vectors_batch)
            put_ms_list.append(put_ms)
            total_vectors_put += len(vectors_batch)
            vectors_batch = []

    # Flush remainder
    if vectors_batch:
        _, put_ms = put_vectors_batch(vectors_batch)
        put_ms_list.append(put_ms)
        total_vectors_put += len(vectors_batch)

    file_total_ms = (time.perf_counter() - file_t0) * 1000.0

    # Update invocation-level aggregates
    stats["files_processed"] += 1
    stats["chunks_total"] += len(chunks)
    stats["vectors_put_total"] += total_vectors_put
    stats["bedrock_retry_total"] += retries_total
    stats["files_with_retries"] += (1 if chunks_with_retry > 0 else 0)

    stats["embed_ms_all"].extend(embed_ms_list)
    stats["put_ms_all"].extend(put_ms_list)
    stats["file_ms_all"].append(file_total_ms)

    return {
        "bucket": bucket,
        "key": key,
        "chunks": len(chunks),
        "vectors_put": total_vectors_put,
        "s3_read_ms": round(s3_read_ms, 2),
        "chunking_ms": round(chunking_ms, 2),
        "file_total_ms": round(file_total_ms, 2),
        "embed_ms_avg": round(mean(embed_ms_list), 2) if embed_ms_list else None,
        "embed_ms_p95": round(pct(embed_ms_list, 95), 2) if embed_ms_list else None,
        "put_calls": len(put_ms_list),
        "put_ms_avg": round(mean(put_ms_list), 2) if put_ms_list else None,
        "put_ms_p95": round(pct(put_ms_list, 95), 2) if put_ms_list else None,
        "retry_count_total": retries_total,
        "chunks_with_retry": chunks_with_retry,
    }