from unittest.mock import Mock

from enterpriseops_ai.ai.understanding import (
    InvestigationContext,
    QuestionUnderstandingService,
)
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState
from enterpriseops_ai.tools.enterprise import EnterpriseTools, SupplierResult


def create_state(
    supplier_name: str | None = None,
) -> InvestigationState:
    return {
        "question": "Why are ACME's orders late?",
        "supplier_name": supplier_name,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": [],
    }


def test_understand_updates_supplier_name() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    understanding_service.understand.return_value = InvestigationContext(
        supplier_name="ACME"
    )
    enterprise_tools = Mock(spec=EnterpriseTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
    )

    state: InvestigationState = create_state()

    update = nodes.understand(state)

    assert update == {"supplier_name": "ACME"}
    understanding_service.understand.assert_called_once_with(
        "Why are ACME's orders late?"
    )


def test_find_supplier_resolves_supplier() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)

    supplier = SupplierResult(
        supplier_id=1,
        tax_id="DE123456789",
        name="ACME",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    enterprise_tools.get_supplier.return_value = supplier

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
    )

    state = create_state(supplier_name="ACME")

    update = nodes.find_supplier(state)

    assert update == {"supplier": supplier}
    enterprise_tools.get_supplier.assert_called_once_with("ACME")


def test_find_supplier_records_error_when_supplier_is_not_found() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    enterprise_tools.get_supplier.return_value = None

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
    )

    state = create_state(supplier_name="UNKNOWN")

    update = nodes.find_supplier(state)

    assert update == {
        "supplier": None,
        "errors": ["Supplier 'UNKNOWN' was not found."],
    }
    enterprise_tools.get_supplier.assert_called_once_with("UNKNOWN")


def test_find_supplier_does_not_query_database_without_supplier_name() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
    )

    state = create_state(supplier_name=None)

    update = nodes.find_supplier(state)

    assert update == {
        "supplier": None,
        "errors": ["No supplier could be identified from the question."],
    }
    enterprise_tools.get_supplier.assert_not_called()
