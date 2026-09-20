from unittest.mock import Mock

from enterpriseops_ai.repositories.document_chunk import RetrievedChunk
from enterpriseops_ai.tools.documents import DocumentTools


def test_search_documents_returns_controlled_document_evidence() -> None:
    retrieval_service = Mock()

    retrieval_service.search.return_value = [
        RetrievedChunk(
            chunk_id=1,
            document_id=10,
            document_title="Supplier Delivery Policy",
            document_source="supplier_delivery_policy.md",
            chunk_index=2,
            content="A delayed purchase order does not automatically establish a root cause.",
            distance=0.24,
        )
    ]

    tools = DocumentTools(retrieval_service)

    result = tools.search_documents(
        question="Why are ACME purchase orders delayed?",
        top_k=3,
    )

    retrieval_service.search.assert_called_once_with(
        question="Why are ACME purchase orders delayed?",
        top_k=3,
    )

    assert len(result) == 1

    evidence = result[0]

    assert evidence.chunk_id == 1
    assert evidence.document_id == 10
    assert evidence.document_title == "Supplier Delivery Policy"
    assert evidence.document_source == "supplier_delivery_policy.md"
    assert evidence.chunk_index == 2
    assert evidence.content == (
        "A delayed purchase order does not automatically establish a root cause."
    )
    assert evidence.distance == 0.24
