from openai import OpenAI


class EmbeddingService:
    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self._client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )

        return [item.embedding for item in response.data]
