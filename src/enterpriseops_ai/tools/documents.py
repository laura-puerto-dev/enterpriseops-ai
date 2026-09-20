from dataclasses import dataclass

from enterpriseops_ai.rag.retrieval import RetrievalService


@dataclass(frozen=True)
class DocumentEvidence:
    chunk_id: int
    document_id: int
    document_title: str
    document_source: str
    chunk_index: int
    content: str
    distance: float


class DocumentTools:
    def __init__(self, retrieval_service: RetrievalService) -> None:
        self.retrieval_service = retrieval_service

    def search_documents(
        self,
        question: str,
        top_k: int = 3,
    ) -> list[DocumentEvidence]:
        chunks = self.retrieval_service.search(
            question=question,
            top_k=top_k,
        )

        return [
            DocumentEvidence(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                document_source=chunk.document_source,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                distance=chunk.distance,
            )
            for chunk in chunks
        ]
