import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from enterpriseops_ai.models import Document, DocumentChunk


def test_document_can_persist_multiple_chunks(
    db_session: Session,
) -> None:
    document = Document(
        title="Supplier Delay Policy",
        source="supplier-delay-policy.md",
    )
    document.chunks = [
        DocumentChunk(
            chunk_index=0,
            content="First chunk",
            embedding=[1.0] + [0.0] * 1535,
        ),
        DocumentChunk(
            chunk_index=1,
            content="Second chunk",
            embedding=[0.0, 1.0] + [0.0] * 1534,
        ),
    ]

    db_session.add(document)
    db_session.flush()

    assert document.id is not None
    assert len(document.chunks) == 2
    assert document.chunks[0].document_id == document.id
    assert document.chunks[1].document_id == document.id


def test_document_rejects_duplicate_chunk_index(
    db_session: Session,
) -> None:
    document = Document(
        title="Supplier Delay Policy",
        source="supplier-delay-policy.md",
    )
    document.chunks = [
        DocumentChunk(
            chunk_index=0,
            content="First chunk",
            embedding=[1.0] + [0.0] * 1535,
        ),
        DocumentChunk(
            chunk_index=0,
            content="Duplicate position",
            embedding=[0.0, 1.0] + [0.0] * 1534,
        ),
    ]

    db_session.add(document)

    with pytest.raises(IntegrityError):
        db_session.flush()
