from unittest.mock import Mock

from enterpriseops_ai.evaluation.golden_dataset import (
    Answerability,
    GoldenDatasetCase,
)
from enterpriseops_ai.evaluation.retrieval_runner import RetrievalEvaluationRunner
from enterpriseops_ai.repositories.document_chunk import RetrievedChunk


def test_evaluate_case_returns_retrieval_result() -> None:
    embedding_service = Mock()
    embedding_service.embed.return_value = [[0.1, 0.2, 0.3]]

    chunk_repository = Mock()
    chunk_repository.search_by_embedding.return_value = [
        RetrievedChunk(
            chunk_id=1,
            document_id=1,
            document_title="Supply Disruption Playbook",
            document_source="supply_disruption_playbook.md",
            chunk_index=0,
            content="Relevant evidence",
            distance=0.25,
        ),
        RetrievedChunk(
            chunk_id=2,
            document_id=2,
            document_title="Supplier Delivery Policy",
            document_source="supplier_delivery_policy.md",
            chunk_index=0,
            content="Other evidence",
            distance=0.45,
        ),
    ]

    case = GoldenDatasetCase(
        id="component-shortage-actions",
        question="What should procurement do when a supplier reports a component shortage?",
        answerability=Answerability.ANSWERABLE,
        expected_sources=["supply_disruption_playbook.md"],
        expected_evidence=["identify affected purchase orders"],
    )

    runner = RetrievalEvaluationRunner(
        embedding_service=embedding_service,
        chunk_repository=chunk_repository,
        top_k=3,
    )

    result = runner.evaluate_case(case)

    embedding_service.embed.assert_called_once_with([case.question])
    chunk_repository.search_by_embedding.assert_called_once_with(
        [0.1, 0.2, 0.3],
        top_k=3,
    )

    assert result.case_id == "component-shortage-actions"
    assert result.answerability == "ANSWERABLE"
    assert result.retrieved_sources == [
        "supply_disruption_playbook.md",
        "supplier_delivery_policy.md",
    ]
    assert result.retrieved_context == [
        "Relevant evidence",
        "Other evidence",
    ]
    assert result.distances == [0.25, 0.45]
    assert result.metrics.source_hit is True
    assert result.metrics.first_relevant_rank == 1
    assert result.latency_ms >= 0
