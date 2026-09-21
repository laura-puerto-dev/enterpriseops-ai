from openai import OpenAI
from sqlalchemy.orm import Session

from enterpriseops_ai.ai.synthesis import SynthesisService
from enterpriseops_ai.ai.understanding import QuestionUnderstandingService
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.rag.retrieval import RetrievalService
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository
from enterpriseops_ai.tools.documents import DocumentTools
from enterpriseops_ai.tools.enterprise import EnterpriseTools


def create_investigation_workflow(
    session: Session,
    openai_api_key: str,
) -> InvestigationWorkflow:
    client = OpenAI(api_key=openai_api_key)

    understanding_service = QuestionUnderstandingService(client=client)
    synthesis_service = SynthesisService(client=client)
    embedding_service = EmbeddingService(api_key=openai_api_key)

    enterprise_tools = EnterpriseTools(session=session)

    document_chunk_repository = DocumentChunkRepository(session=session)
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        repository=document_chunk_repository,
    )
    document_tools = DocumentTools(
        retrieval_service=retrieval_service,
    )

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
        synthesis_service=synthesis_service,
    )

    return InvestigationWorkflow(nodes=nodes)
