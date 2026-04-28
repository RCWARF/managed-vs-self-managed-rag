def build_context_text(vectors: list[dict]) -> str:
    return "\n\n---\n\n".join(
        (vector.get("metadata") or {}).get("content", "")
        for vector in vectors
    )


def build_qa_prompt(question: str, context_text: str) -> str:
    return (
        "Answer the following question using ONLY the context provided below. "
        "If the answer cannot be found in the context, say "
        "\"I don't have enough information to answer that question.\"\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )