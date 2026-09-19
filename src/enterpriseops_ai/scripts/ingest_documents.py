from pathlib import Path

from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.rag.chunking import DocumentChunker
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.rag.ingestion import DocumentIngestionService

DOCUMENTS_DIRECTORY = Path("data/documents")


def main() -> None:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for document ingestion")

    chunker = DocumentChunker()
    embedding_service = EmbeddingService(api_key=settings.openai_api_key)

    with SessionFactory() as session:
        ingestion_service = DocumentIngestionService(
            session=session,
            chunker=chunker,
            embedding_service=embedding_service,
        )

        for path in sorted(DOCUMENTS_DIRECTORY.glob("*.md")):
            content = path.read_text(encoding="utf-8")

            document = ingestion_service.ingest(
                title=path.stem.replace("_", " ").title(),
                source=path.name,
                content=content,
            )

            print(f"Ingested {path.name}: {len(document.chunks)} chunks")

        session.commit()


if __name__ == "__main__":
    main()
