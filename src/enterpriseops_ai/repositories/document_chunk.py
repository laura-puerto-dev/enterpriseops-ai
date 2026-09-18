from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from enterpriseops_ai.models import Document, DocumentChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_title: str
    document_source: str
    chunk_index: int
    content: str
    distance: float


class DocumentChunkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_by_embedding(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        distance = DocumentChunk.embedding.cosine_distance(query_embedding).label(
            "distance"
        )

        statement = (
            select(DocumentChunk, Document, distance)
            .join(Document, DocumentChunk.document_id == Document.id)
            .order_by(distance)
            .limit(top_k)
        )

        rows = self.session.execute(statement).all()

        return [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=document.id,
                document_title=document.title,
                document_source=document.source,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                distance=float(chunk_distance),
            )
            for chunk, document, chunk_distance in rows
        ]
