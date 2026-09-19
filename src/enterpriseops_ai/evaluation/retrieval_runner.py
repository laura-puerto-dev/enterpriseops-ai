from dataclasses import dataclass
from time import perf_counter

from enterpriseops_ai.evaluation.golden_dataset import GoldenDatasetCase
from enterpriseops_ai.evaluation.retrieval_metrics import (
    RetrievalMetrics,
    calculate_retrieval_metrics,
)
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    case_id: str
    question: str
    answerability: str
    retrieved_sources: list[str]
    distances: list[float]
    latency_ms: float
    metrics: RetrievalMetrics


class RetrievalEvaluationRunner:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        chunk_repository: DocumentChunkRepository,
        *,
        top_k: int = 3,
    ) -> None:
        self._embedding_service = embedding_service
        self._chunk_repository = chunk_repository
        self._top_k = top_k

    def evaluate_case(
        self,
        case: GoldenDatasetCase,
    ) -> RetrievalEvaluationResult:
        start = perf_counter()

        query_embedding = self._embedding_service.embed([case.question])[0]

        retrieved_chunks = self._chunk_repository.search_by_embedding(
            query_embedding,
            top_k=self._top_k,
        )

        latency_ms = (perf_counter() - start) * 1000

        retrieved_sources = [chunk.document_source for chunk in retrieved_chunks]

        metrics = calculate_retrieval_metrics(
            expected_sources=case.expected_sources,
            retrieved_sources=retrieved_sources,
        )

        return RetrievalEvaluationResult(
            case_id=case.id,
            question=case.question,
            answerability=case.answerability.value,
            retrieved_sources=retrieved_sources,
            distances=[chunk.distance for chunk in retrieved_chunks],
            latency_ms=latency_ms,
            metrics=metrics,
        )
