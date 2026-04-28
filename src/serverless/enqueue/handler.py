###This takes objects from s3 and formats them for sqs so downstream ingestion function can handle data types###
#cloud_function(platforms=[Platform.AWS], memory=512, config=config)
def yourFunction(request, context):
    import json
    import boto3
    import os
    import hashlib
    from urllib.parse import unquote_plus
    from Inspector import Inspector

    inspector = Inspector()
    #inspector.inspectAll()

    sqs = boto3.client("sqs")
    QUEUE_URL = os.environ["QUEUE_URL"]

    records = request.get("Records", [])
    inspector.addAttribute("num_s3_records", len(records))

    batch = []
    sent = 0
    failed = 0

    for i, rec in enumerate(records):
        bucket = rec["s3"]["bucket"]["name"]
        key = unquote_plus(rec["s3"]["object"]["key"])

        event_time = rec.get("eventTime")
        etag = rec.get("s3", {}).get("object", {}).get("eTag")
        size = rec.get("s3", {}).get("object", {}).get("size")
        sequencer = rec.get("s3", {}).get("object", {}).get("sequencer")

        msg = {
            "bucket": bucket,
            "key": key,
            "eventTime": event_time,
            "etag": etag,
            "size": size,
            "sequencer": sequencer,
            "source": "s3_event"
        }

        body = json.dumps(msg)

        # FIFO: choose a grouping strategy
        # Option A: keep all docs in one group (strict ordering, lowest throughput)
        # group_id = "rag-ingest"
        #
        # Option B (recommended): group by file so one file is ordered, multiple files can run in parallel
        
        group_id = hashlib.sha256(f"{bucket}:{key}".encode()).hexdigest()[:128]


        # FIFO dedup id (good even if you enabled content-based dedup)
        #dedup_seed = f"{bucket}:{key}:{etag}"
        #could use dedup_seed here instead of body in dedup_id
        #but I want reuploads to trigger even if the file is unchanged
        dedup_id = hashlib.sha256(body.encode("utf-8")).hexdigest()

        batch.append({
            "Id": str(i),  # unique within the batch
            "MessageBody": body,
            "MessageGroupId": group_id,
            "MessageDeduplicationId": dedup_id,
        })

        if len(batch) == 10:
            resp = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
            sent += len(resp.get("Successful", []))
            failed += len(resp.get("Failed", []))
            batch = []

    if batch:
        resp = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
        sent += len(resp.get("Successful", []))
        failed += len(resp.get("Failed", []))

    inspector.addAttribute("messages_sent", sent)
    inspector.addAttribute("messages_failed", failed)

    #inspector.inspectAllDeltas()
    output = inspector.finish()
    print(json.dumps(output))
    return output
