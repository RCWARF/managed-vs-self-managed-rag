from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class QueryRequest:
    question: str
    top_k: int = 3
    debug: bool = False
    metadata_filter: Optional[dict[str, Any]] = None