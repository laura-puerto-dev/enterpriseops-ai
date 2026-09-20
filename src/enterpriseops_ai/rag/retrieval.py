from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.repositories.document_chunk import (
    DocumentChunkRepository,
    RetrievedChunk,
)


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
        query_embedding = self.embedding_service.embed([question])[0]

        return self.repository.search_by_embedding(
            query_embedding=query_embedding,
            top_k=top_k,
        )
