import sys

from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.rag.retrieval import RetrievalService
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository


def main() -> None:
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Provide a question, for example: "
            "python -m enterpriseops_ai.scripts.search_documents "
            '"What should procurement do about repeated supplier delays?"'
        )

    question = sys.argv[1]

    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for semantic search")

    embedding_service = EmbeddingService(api_key=settings.openai_api_key)

    with SessionFactory() as session:
        repository = DocumentChunkRepository(session)
        retrieval_service = RetrievalService(
            embedding_service=embedding_service,
            repository=repository,
        )
        results = retrieval_service.search(
            question=question,
            top_k=3,
        )

        print(f"\nQuestion: {question}\n")

        for position, result in enumerate(results, start=1):
            print(f"--- Result {position} ---")
            print(f"Document: {result.document_title}")
            print(f"Source: {result.document_source}")
            print(f"Chunk: {result.chunk_index}")
            print(f"Distance: {result.distance:.4f}")
            print(result.content)
            print()


if __name__ == "__main__":
    main()
