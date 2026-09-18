from sqlalchemy.orm import Session

from enterpriseops_ai.models import Document, DocumentChunk
from enterpriseops_ai.rag.chunking import DocumentChunker
from enterpriseops_ai.rag.embeddings import EmbeddingService


class DocumentIngestionService:
    def __init__(
        self,
        session: Session,
        chunker: DocumentChunker,
        embedding_service: EmbeddingService,
    ) -> None:
        self.session = session
        self.chunker = chunker
        self.embedding_service = embedding_service

    def ingest(
        self,
        *,
        title: str,
        source: str,
        content: str,
    ) -> Document:
        chunks = self.chunker.split(content)
        embeddings = self.embedding_service.embed(chunks)

        document = Document(
            title=title,
            source=source,
            chunks=[
                DocumentChunk(
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                )
                for index, (chunk, embedding) in enumerate(
                    zip(chunks, embeddings, strict=True)
                )
            ],
        )

        self.session.add(document)
        self.session.flush()

        return document
