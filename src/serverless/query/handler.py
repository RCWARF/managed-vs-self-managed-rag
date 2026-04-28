from Inspector import Inspector

from clients import create_bedrock_client, create_s3vectors_client
from config import AppConfig
from services.embedding_service import EmbeddingService
from services.generation_service import GenerationService
from services.vector_service import VectorSearchService
from utils.request_parser import parse_request
from utils.response_builder import (
    finish_debug,
    finish_error,
    finish_no_results,
    finish_success,
)


def yourFunction(request, context):
    inspector = Inspector()

    try:
        config = AppConfig.from_env()
        query_request = parse_request(request)

        inspector.addAttribute("debug", query_request.debug)
        inspector.addAttribute("vector_bucket", config.vector_bucket)
        inspector.addAttribute("vector_index", config.vector_index)
        inspector.addAttribute("top_k", query_request.top_k)

        if query_request.debug:
            return finish_debug(inspector)

        if not query_request.question:
            return finish_error(inspector, "Question missing")

        bedrock_client = create_bedrock_client(config)
        s3vectors_client = create_s3vectors_client(config)

        embedding_service = EmbeddingService(
            bedrock_client=bedrock_client,
            model_id=config.embed_model_id,
            inspector=inspector,
        )

        vector_service = VectorSearchService(
            s3vectors_client=s3vectors_client,
            vector_bucket=config.vector_bucket,
            vector_index=config.vector_index,
            inspector=inspector,
        )

        generation_service = GenerationService(
            bedrock_client=bedrock_client,
            model_id=config.query_model_id,
            inspector=inspector,
        )

        embedding = embedding_service.get_embedding(query_request.question)

        vectors = vector_service.search(
            embedding=embedding,
            top_k=query_request.top_k,
            metadata_filter=query_request.metadata_filter,
        )

        if not vectors:
            return finish_no_results(inspector)

        answer = generation_service.answer_question(
            question=query_request.question,
            vectors=vectors,
        )

        return finish_success(inspector, answer, vectors)

    except Exception as exc:
        return finish_error(inspector, str(exc))