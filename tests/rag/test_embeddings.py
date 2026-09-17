from unittest.mock import MagicMock

from enterpriseops_ai.rag.embeddings import EmbeddingService


def test_embed_returns_embeddings_for_multiple_texts() -> None:
    client = MagicMock()
    client.embeddings.create.return_value.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
        MagicMock(embedding=[0.4, 0.5, 0.6]),
    ]

    service = EmbeddingService(api_key="test-key")
    service._client = client

    result = service.embed(["first chunk", "second chunk"])

    client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input=["first chunk", "second chunk"],
    )
    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]


def test_embed_returns_empty_list_without_calling_openai() -> None:
    client = MagicMock()

    service = EmbeddingService(api_key="test-key")
    service._client = client

    result = service.embed([])

    assert result == []
    client.embeddings.create.assert_not_called()
