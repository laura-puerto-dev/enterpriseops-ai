from sqlalchemy.orm import Session

from enterpriseops_ai.models import Document, DocumentChunk
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository


def _vector(first: float, second: float) -> list[float]:
    return [first, second] + [0.0] * 1534


def test_search_by_embedding_orders_chunks_by_cosine_distance(
    db_session: Session,
) -> None:
    document = Document(
        title="Supplier Operations Policy",
        source="supplier-operations-policy.md",
        chunks=[
            DocumentChunk(
                chunk_index=0,
                content="Supplier delivery information",
                embedding=_vector(1.0, 0.0),
            ),
            DocumentChunk(
                chunk_index=1,
                content="Unrelated quality information",
                embedding=_vector(0.0, 1.0),
            ),
        ],
    )

    db_session.add(document)
    db_session.flush()

    repository = DocumentChunkRepository(db_session)

    results = repository.search_by_embedding(
        query_embedding=_vector(1.0, 0.0),
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].content == "Supplier delivery information"
    assert results[0].document_title == "Supplier Operations Policy"
    assert results[0].document_source == "supplier-operations-policy.md"
    assert results[0].distance == 0.0

    assert results[1].content == "Unrelated quality information"
    assert results[1].distance > results[0].distance
