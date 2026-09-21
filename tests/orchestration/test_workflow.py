from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from enterpriseops_ai.ai.understanding import (
    InvestigationContext,
    QuestionUnderstandingService,
)
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow
from enterpriseops_ai.tools.documents import DocumentEvidence, DocumentTools
from enterpriseops_ai.tools.enterprise import (
    EnterpriseTools,
    PurchaseOrderResult,
    ServiceTicketResult,
    SupplierResult,
)


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

    purchase_order = PurchaseOrderResult(
        purchase_order_id=10,
        order_number="PO-001",
        status="delayed",
        ordered_at=date(2026, 9, 1),
        expected_delivery_date=date(2026, 9, 15),
        actual_delivery_date=None,
        total_amount=Decimal("1250.00"),
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

    enterprise_tools = Mock(spec=EnterpriseTools)
    enterprise_tools.get_supplier.return_value = supplier
    enterprise_tools.search_purchase_orders.return_value = [purchase_order]
    enterprise_tools.search_service_tickets.return_value = [service_ticket]

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
    assert result["purchase_orders"] == [purchase_order]
    assert result["service_tickets"] == [service_ticket]
    assert result["documents"] == [document]
    assert result["answer"] is None
    assert result["errors"] == []

    enterprise_tools.get_supplier.assert_called_once_with("ACME")
    enterprise_tools.search_purchase_orders.assert_called_once_with(
        supplier.supplier_id
    )
    enterprise_tools.search_service_tickets.assert_called_once_with(
        supplier.supplier_id
    )
    document_tools.search_documents.assert_called_once_with(
        question="Why are ACME's orders late?",
    )


def test_workflow_skips_structured_tools_when_supplier_is_not_resolved() -> None:
    understanding_service = Mock(spec=QuestionUnderstandingService)
    understanding_service.understand.return_value = InvestigationContext(
        supplier_name=None,
    )

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
    workflow = InvestigationWorkflow(nodes=nodes)

    initial_state: InvestigationState = {
        "question": "Why are these purchase orders late?",
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": ["Previous warning."],
    }

    result = workflow.invoke(initial_state)

    assert result["supplier_name"] is None
    assert result["supplier"] is None
    assert result["purchase_orders"] == []
    assert result["service_tickets"] == []
    assert result["documents"] == [document]
    assert result["errors"] == [
        "Previous warning.",
        "No supplier could be identified from the question.",
    ]

    enterprise_tools.get_supplier.assert_not_called()
    enterprise_tools.search_purchase_orders.assert_not_called()
    enterprise_tools.search_service_tickets.assert_not_called()
    document_tools.search_documents.assert_called_once_with(
        question="Why are these purchase orders late?",
    )
