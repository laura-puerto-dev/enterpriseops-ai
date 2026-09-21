from enterpriseops_ai.ai.synthesis import SynthesisService
from enterpriseops_ai.ai.understanding import QuestionUnderstandingService
from enterpriseops_ai.orchestration.state import (
    InvestigationState,
    InvestigationStateUpdate,
)
from enterpriseops_ai.tools.documents import DocumentTools
from enterpriseops_ai.tools.enterprise import EnterpriseTools


class InvestigationNodes:
    def __init__(
        self,
        understanding_service: QuestionUnderstandingService,
        enterprise_tools: EnterpriseTools,
        document_tools: DocumentTools,
        synthesis_service: SynthesisService,
    ) -> None:
        self.understanding_service = understanding_service
        self.enterprise_tools = enterprise_tools
        self.document_tools = document_tools
        self.synthesis_service = synthesis_service

    def understand(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        context = self.understanding_service.understand(state["question"])

        return {
            "supplier_name": context.supplier_name,
        }

    def find_supplier(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        supplier_name = state["supplier_name"]

        if supplier_name is None:
            return {
                "supplier": None,
                "errors": ["No supplier could be identified from the question."],
            }

        supplier = self.enterprise_tools.get_supplier(supplier_name)

        if supplier is None:
            return {
                "supplier": None,
                "errors": [f"Supplier '{supplier_name}' was not found."],
            }

        return {
            "supplier": supplier,
        }

    def search_purchase_orders(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        supplier = state["supplier"]

        if supplier is None:
            return {
                "purchase_orders": [],
                "errors": [
                    "Purchase orders could not be searched without a resolved supplier."
                ],
            }

        purchase_orders = self.enterprise_tools.search_purchase_orders(
            supplier.supplier_id
        )

        return {
            "purchase_orders": purchase_orders,
        }

    def search_service_tickets(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        supplier = state["supplier"]

        if supplier is None:
            return {
                "service_tickets": [],
                "errors": [
                    "Service tickets could not be searched without a resolved supplier."
                ],
            }

        service_tickets = self.enterprise_tools.search_service_tickets(
            supplier.supplier_id
        )

        return {
            "service_tickets": service_tickets,
        }

    def search_documents(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        documents = self.document_tools.search_documents(
            question=state["question"],
        )

        return {
            "documents": documents,
        }

    def route_after_supplier(
        self,
        state: InvestigationState,
    ) -> str:
        if state["supplier"] is None:
            return "search_documents"

        return "search_purchase_orders"

    def synthesize(
        self,
        state: InvestigationState,
    ) -> InvestigationStateUpdate:
        answer = self.synthesis_service.synthesize(
            question=state["question"],
            supplier=state["supplier"],
            purchase_orders=state["purchase_orders"],
            service_tickets=state["service_tickets"],
            documents=state["documents"],
            errors=state["errors"],
        )

        return {
            "answer": answer,
        }
