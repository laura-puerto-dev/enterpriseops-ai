from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from enterpriseops_ai.rag.chunking import DocumentChunker
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.rag.ingestion import DocumentIngestionService


def test_ingest_creates_document_with_embedded_chunks(
    db_session: Session,
) -> None:
    chunker = MagicMock(spec=DocumentChunker)
    chunker.split.return_value = [
        "First procurement policy chunk",
        "Second procurement policy chunk",
    ]

    embedding_service = MagicMock(spec=EmbeddingService)
    embedding_service.embed.return_value = [
        [1.0] + [0.0] * 1535,
        [0.0, 1.0] + [0.0] * 1534,
    ]

    service = DocumentIngestionService(
        session=db_session,
        chunker=chunker,
        embedding_service=embedding_service,
    )

    document = service.ingest(
        title="Procurement Policy",
        source="procurement_policy.md",
        content="Full procurement policy content",
    )

    chunker.split.assert_called_once_with("Full procurement policy content")
    embedding_service.embed.assert_called_once_with(
        [
            "First procurement policy chunk",
            "Second procurement policy chunk",
        ]
    )

    assert document.id is not None
    assert document.title == "Procurement Policy"
    assert document.source == "procurement_policy.md"

    assert len(document.chunks) == 2

    assert document.chunks[0].chunk_index == 0
    assert document.chunks[0].content == "First procurement policy chunk"
    assert document.chunks[0].embedding == [1.0] + [0.0] * 1535

    assert document.chunks[1].chunk_index == 1
    assert document.chunks[1].content == "Second procurement policy chunk"
    assert document.chunks[1].embedding == [0.0, 1.0] + [0.0] * 1534


def test_ingest_fails_when_embedding_count_does_not_match_chunk_count(
    db_session: Session,
) -> None:
    chunker = MagicMock(spec=DocumentChunker)
    chunker.split.return_value = [
        "First chunk",
        "Second chunk",
    ]

    embedding_service = MagicMock(spec=EmbeddingService)
    embedding_service.embed.return_value = [
        [1.0] + [0.0] * 1535,
    ]

    service = DocumentIngestionService(
        session=db_session,
        chunker=chunker,
        embedding_service=embedding_service,
    )

    with pytest.raises(ValueError):
        service.ingest(
            title="Procurement Policy",
            source="procurement_policy.md",
            content="Full procurement policy content",
        )
