def yourFunction(request, context):

    import time
    import json
    from statistics import mean

    from .Inspector import Inspector
    from .processor import process_one_message, pct

    from .config import (
        VECTOR_BUCKET,
        VECTOR_INDEX,
        MODEL_ID,
        PUT_BATCH_SIZE
    )
    # -------- Main (SQS event) --------
    inspector = Inspector()
    batch_failures = []
    results = []

    inv_t0 = time.perf_counter()

    stats = {
        "files_processed": 0,
        "chunks_total": 0,
        "vectors_put_total": 0,
        "bedrock_retry_total": 0,
        "files_with_retries": 0,
        "embed_ms_all": [],
        "put_ms_all": [],
        "file_ms_all": [],
    }

    try:
        records = request.get("Records", [])
        inspector.addAttribute("num_sqs_records", len(records))
        inspector.addAttribute("vector_bucket", VECTOR_BUCKET)
        inspector.addAttribute("vector_index", VECTOR_INDEX)
        inspector.addAttribute("embed_model_id", MODEL_ID)
        inspector.addAttribute("put_batch_size", PUT_BATCH_SIZE)

        for rec in records:
            message_id = rec.get("messageId", "unknown")
            try:
                msg_body = json.loads(rec["body"])
                if not msg_body.get("bucket") or not msg_body.get("key") or not msg_body.get("etag"):
                    raise ValueError(f"Missing required fields in SQS body: {msg_body}")
                bucket = msg_body.get("bucket")
                key = msg_body.get("key")
                

                inspector.addAttribute("current_bucket", bucket)
                inspector.addAttribute("current_file_key", key)

                r = process_one_message(msg_body, stats)
                results.append({"messageId": message_id, "result": r})

            except Exception as e:
                batch_failures.append({"itemIdentifier": message_id})
                results.append({"messageId": message_id, "error": str(e)})

        inv_total_ms = (time.perf_counter() - inv_t0) * 1000.0

        inspector.addAttribute("files_processed", stats["files_processed"])
        inspector.addAttribute("chunks_total", stats["chunks_total"])
        inspector.addAttribute("vectors_put_total", stats["vectors_put_total"])
        inspector.addAttribute("invocation_total_ms", round(inv_total_ms, 2))

        if stats["embed_ms_all"]:
            inspector.addAttribute("embed_ms_p50_all", round(pct(stats["embed_ms_all"], 50), 2))
            inspector.addAttribute("embed_ms_p95_all", round(pct(stats["embed_ms_all"], 95), 2))
            inspector.addAttribute("embed_ms_avg_all", round(mean(stats["embed_ms_all"]), 2))

        if stats["put_ms_all"]:
            inspector.addAttribute("put_ms_p95_all", round(pct(stats["put_ms_all"], 95), 2))
            inspector.addAttribute("put_ms_avg_all", round(mean(stats["put_ms_all"]), 2))

        if stats["file_ms_all"]:
            inspector.addAttribute("file_ms_avg", round(mean(stats["file_ms_all"]), 2))
            inspector.addAttribute("file_ms_p95", round(pct(stats["file_ms_all"], 95), 2))

        inspector.addAttribute("bedrock_retry_total", stats["bedrock_retry_total"])
        inspector.addAttribute("files_with_retries", stats["files_with_retries"])
        inspector.addAttribute("messages_ok", len(records) - len(batch_failures))
        inspector.addAttribute("messages_failed", len(batch_failures))
        inspector.addAttribute("status", "partial_success" if batch_failures else "success")

        return {"batchItemFailures": batch_failures, "results": results}

    finally:
        print(json.dumps(inspector.finish()))