from enterpriseops_ai.ai.understanding import QuestionUnderstandingService
from enterpriseops_ai.orchestration.state import (
    InvestigationState,
    InvestigationStateUpdate,
)
from enterpriseops_ai.tools.enterprise import EnterpriseTools


class InvestigationNodes:
    def __init__(
        self,
        understanding_service: QuestionUnderstandingService,
        enterprise_tools: EnterpriseTools,
    ) -> None:
        self.understanding_service = understanding_service
        self.enterprise_tools = enterprise_tools

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
