from unittest.mock import Mock

from enterpriseops_ai.ai.understanding import (
    InvestigationContext,
    QuestionUnderstandingService,
)
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow
from enterpriseops_ai.tools.enterprise import EnterpriseTools, SupplierResult


def test_workflow_understands_and_resolves_supplier() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    understanding_service.understand.return_value = InvestigationContext(
        supplier_name="ACME"
    )

    supplier = SupplierResult(
        supplier_id=1,
        tax_id="DE123456789",
        name="ACME",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    enterprise_tools = Mock(spec=EnterpriseTools)
    enterprise_tools.get_supplier.return_value = supplier

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
    )
    workflow = InvestigationWorkflow(nodes=nodes)

    state: InvestigationState = {
        "question": "Why are ACME's orders late?",
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": [],
    }

    result = workflow.invoke(state)

    assert result["question"] == "Why are ACME's orders late?"
    assert result["supplier_name"] == "ACME"
    assert result["supplier"] == supplier
    assert result["purchase_orders"] == []
    assert result["service_tickets"] == []
    assert result["documents"] == []
    assert result["answer"] is None
    assert result["errors"] == []
