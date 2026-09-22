from time import perf_counter

import structlog

from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.repositories.document_chunk import (
    DocumentChunkRepository,
    RetrievedChunk,
)

logger = structlog.get_logger()


class RetrievalService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        repository: DocumentChunkRepository,
    ) -> None:
        self.embedding_service = embedding_service
        self.repository = repository

    def search(
        self,
        question: str,
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        start_time = perf_counter()

        query_embedding = self.embedding_service.embed([question])[0]

        chunks = self.repository.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        logger.info(
            "retrieval_completed",
            duration_ms=round((perf_counter() - start_time) * 1000, 2),
            top_k=top_k,
            chunks_retrieved=len(chunks),
        )

        return chunks
