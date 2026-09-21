from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from enterpriseops_ai.ai.understanding import (
    InvestigationContext,
    QuestionUnderstandingService,
)
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState
from enterpriseops_ai.tools.documents import DocumentEvidence, DocumentTools
from enterpriseops_ai.tools.enterprise import (
    EnterpriseTools,
    PurchaseOrderResult,
    ServiceTicketResult,
    SupplierResult,
)


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
    document_tools = Mock(spec=DocumentTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
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
    document_tools = Mock(spec=DocumentTools)

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
        document_tools=document_tools,
    )

    state = create_state(supplier_name="ACME")

    update = nodes.find_supplier(state)

    assert update == {"supplier": supplier}
    enterprise_tools.get_supplier.assert_called_once_with("ACME")


def test_find_supplier_records_error_when_supplier_is_not_found() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)
    enterprise_tools.get_supplier.return_value = None

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
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
    document_tools = Mock(spec=DocumentTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state(supplier_name=None)

    update = nodes.find_supplier(state)

    assert update == {
        "supplier": None,
        "errors": ["No supplier could be identified from the question."],
    }
    enterprise_tools.get_supplier.assert_not_called()


def test_search_purchase_orders_returns_delayed_orders() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)

    supplier = SupplierResult(
        supplier_id=1,
        tax_id="DE123456789",
        name="ACME",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    purchase_order = PurchaseOrderResult(
        purchase_order_id=10,
        order_number="PO-001",
        status="delayed",
        ordered_at=date(2026, 9, 1),
        expected_delivery_date=date(2026, 9, 15),
        actual_delivery_date=None,
        total_amount=Decimal("1250.00"),
    )
    enterprise_tools.search_purchase_orders.return_value = [purchase_order]

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state()
    state["supplier"] = supplier

    update = nodes.search_purchase_orders(state)

    assert update == {"purchase_orders": [purchase_order]}
    enterprise_tools.search_purchase_orders.assert_called_once_with(
        supplier.supplier_id
    )


def test_search_purchase_orders_does_not_query_without_supplier() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state()

    update = nodes.search_purchase_orders(state)

    assert update == {
        "purchase_orders": [],
        "errors": [
            "Purchase orders could not be searched without a resolved supplier."
        ],
    }
    enterprise_tools.search_purchase_orders.assert_not_called()


def test_search_service_tickets_returns_supplier_tickets() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)

    supplier = SupplierResult(
        supplier_id=1,
        tax_id="DE123456789",
        name="ACME",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    service_ticket = ServiceTicketResult(
        ticket_id=20,
        purchase_order_id=10,
        title="Supplier capacity issue",
        description="Supplier reported reduced production capacity.",
        status="open",
        priority="high",
        resolved_at=None,
    )
    enterprise_tools.search_service_tickets.return_value = [service_ticket]

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state()
    state["supplier"] = supplier

    update = nodes.search_service_tickets(state)

    assert update == {"service_tickets": [service_ticket]}
    enterprise_tools.search_service_tickets.assert_called_once_with(
        supplier.supplier_id
    )


def test_search_service_tickets_does_not_query_without_supplier() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state()

    update = nodes.search_service_tickets(state)

    assert update == {
        "service_tickets": [],
        "errors": [
            "Service tickets could not be searched without a resolved supplier."
        ],
    }
    enterprise_tools.search_service_tickets.assert_not_called()


def test_search_documents_returns_retrieved_evidence() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    enterprise_tools = Mock(spec=EnterpriseTools)
    document_tools = Mock(spec=DocumentTools)

    document = DocumentEvidence(
        chunk_id=1,
        document_id=10,
        document_title="Supplier Delivery Policy",
        document_source="supplier_delivery_policy.md",
        chunk_index=0,
        content="Delayed deliveries must be investigated with the supplier.",
        distance=0.25,
    )
    document_tools.search_documents.return_value = [document]

    nodes = InvestigationNodes(
        understanding_service=understanding_service,
        enterprise_tools=enterprise_tools,
        document_tools=document_tools,
    )

    state = create_state()

    update = nodes.search_documents(state)

    assert update == {"documents": [document]}
    document_tools.search_documents.assert_called_once_with(
        question="Why are ACME's orders late?",
    )
