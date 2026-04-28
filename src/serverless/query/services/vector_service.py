import time


class VectorSearchService:
    def __init__(self, s3vectors_client, vector_bucket: str, vector_index: str, inspector):
        self.s3vectors = s3vectors_client
        self.vector_bucket = vector_bucket
        self.vector_index = vector_index
        self.inspector = inspector

    def search(self, embedding: list[float], top_k: int = 3, metadata_filter=None) -> list[dict]:
        kwargs = {
            "vectorBucketName": self.vector_bucket,
            "indexName": self.vector_index,
            "topK": top_k,
            "queryVector": {"float32": embedding},
            "returnMetadata": True,
            "returnDistance": True,
        }

        if metadata_filter is not None:
            kwargs["filter"] = metadata_filter

        t0 = time.perf_counter()
        response = self.s3vectors.query_vectors(**kwargs)
        t1 = time.perf_counter()

        vectors = response.get("vectors", [])

        self.inspector.addAttribute("vector_search_rtt_ms", round((t1 - t0) * 1000, 2))
        self.inspector.addAttribute("top_distances", [v.get("distance") for v in vectors[:5]])
        self.inspector.addAttribute("distance_metric", response.get("distanceMetric"))
        self.inspector.addAttribute("docs_retrieved", len(vectors))

        return vectors