import json
import time
from utils.prompt_builder import build_context_text, build_qa_prompt


class GenerationService:
    def __init__(self, bedrock_client, model_id: str, inspector):
        self.bedrock = bedrock_client
        self.model_id = model_id
        self.inspector = inspector

    def answer_question(self, question: str, vectors: list[dict]) -> str:
        context_text = build_context_text(vectors)
        prompt = build_qa_prompt(question, context_text)

        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7,
                "topP": 0.9,
            },
        }

        t0 = time.perf_counter()
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
        )
        response_body = response["body"].read()
        t1 = time.perf_counter()

        answer = json.loads(response_body)["output"]["message"]["content"][0]["text"]

        self.inspector.addAttribute("query_rtt_ms", round((t1 - t0) * 1000, 2))
        self.inspector.addAttribute("prompt_length", len(prompt))
        self.inspector.addAttribute("answer_length", len(answer))
        self.inspector.addAttribute("num_docs_used", len(vectors))

        return answer