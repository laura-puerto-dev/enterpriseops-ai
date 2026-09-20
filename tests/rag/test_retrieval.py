from unittest.mock import Mock

from enterpriseops_ai.rag.retrieval import RetrievalService
from enterpriseops_ai.repositories.document_chunk import RetrievedChunk


def test_search_embeds_question_and_retrieves_chunks() -> None:
    embedding_service = Mock()
    repository = Mock()

    embedding_service.embed.return_value = [[0.1, 0.2, 0.3]]

    expected_chunks = [
        RetrievedChunk(
            chunk_id=1,
            document_id=10,
            document_title="Supplier Delivery Policy",
            document_source="supplier_delivery_policy.md",
            chunk_index=0,
            content="Delayed purchase orders require investigation.",
            distance=0.25,
        )
    ]

    repository.search_by_embedding.return_value = expected_chunks

    service = RetrievalService(
        embedding_service=embedding_service,
        repository=repository,
    )

    result = service.search(
        question="Why are the purchase orders delayed?",
        top_k=3,
    )

    embedding_service.embed.assert_called_once_with(
        ["Why are the purchase orders delayed?"]
    )
    repository.search_by_embedding.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=3,
    )
    assert result == expected_chunks
