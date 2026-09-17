from openai import OpenAI


class EmbeddingService:
    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self._client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )

        return [item.embedding for item in response.data]
