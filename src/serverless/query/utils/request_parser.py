import json
from models import QueryRequest


def parse_request(event: dict) -> QueryRequest:
    raw_body = event.get("body", {})

    if isinstance(raw_body, str):
        body = json.loads(raw_body or "{}")
    elif isinstance(raw_body, dict):
        body = raw_body
    else:
        body = {}

    question = (body.get("question") or "").strip()
    top_k = int(body.get("top_k", 3))
    debug = bool(body.get("debug", False))

    metadata_filter = None
    if body.get("etag"):
        metadata_filter = {"etag": body["etag"]}

    return QueryRequest(
        question=question,
        top_k=top_k,
        debug=debug,
        metadata_filter=metadata_filter,
    )