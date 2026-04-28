import json
import time


class EmbeddingService:
    def __init__(self, bedrock_client, model_id: str, inspector):
        self.bedrock = bedrock_client
        self.model_id = model_id
        self.inspector = inspector

    def get_embedding(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text[:8000]})

        t0 = time.perf_counter()
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body,
        )
        response_body = response["body"].read()
        t1 = time.perf_counter()

        embedding = json.loads(response_body)["embedding"]

        self.inspector.addAttribute("embedding_length", len(embedding))
        self.inspector.addAttribute("embedding_rtt_ms", round((t1 - t0) * 1000, 2))

        return embedding