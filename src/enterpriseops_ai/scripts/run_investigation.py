from openai import OpenAI

from enterpriseops_ai.ai.synthesis import SynthesisService
from enterpriseops_ai.ai.understanding import QuestionUnderstandingService
from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.rag.retrieval import RetrievalService
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository
from enterpriseops_ai.tools.documents import DocumentTools
from enterpriseops_ai.tools.enterprise import EnterpriseTools


def main() -> None:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is required to run an investigation.")

    client = OpenAI(api_key=settings.openai_api_key)

    understanding_service = QuestionUnderstandingService(client=client)
    synthesis_service = SynthesisService(client=client)
    embedding_service = EmbeddingService(api_key=settings.openai_api_key)

    with SessionFactory() as session:
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

        workflow = InvestigationWorkflow(nodes=nodes)

        initial_state: InvestigationState = {
            "question": "Why are purchase orders from supplier ACME being delayed?",
            "supplier_name": None,
            "supplier": None,
            "purchase_orders": [],
            "service_tickets": [],
            "documents": [],
            "answer": None,
            "errors": [],
        }

        result = workflow.invoke(initial_state)

        print("\n=== INVESTIGATION RESULT ===\n")
        print(
            result["answer"].model_dump_json(indent=2)
            if result["answer"]
            else "No answer"
        )

        print("\n=== WORKFLOW ERRORS ===\n")
        print(result["errors"])


if __name__ == "__main__":
    main()
