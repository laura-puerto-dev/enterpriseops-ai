from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from enterpriseops_ai.models import PurchaseOrder, ServiceTicket, Supplier
from enterpriseops_ai.tools.enterprise import EnterpriseTools


def test_get_supplier_returns_controlled_supplier_result(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE555555555",
        name="Enterprise Tool Supplier",
        status="active",
        country="DE",
        lead_time_days=12,
    )

    db_session.add(supplier)
    db_session.flush()

    tools = EnterpriseTools(db_session)

    result = tools.get_supplier("enterprise tool supplier")

    assert result is not None
    assert result.supplier_id == supplier.id
    assert result.tax_id == "DE555555555"
    assert result.name == "Enterprise Tool Supplier"
    assert result.status == "active"
    assert result.country == "DE"
    assert result.lead_time_days == 12


def test_get_supplier_returns_none_when_supplier_does_not_exist(
    db_session: Session,
) -> None:
    tools = EnterpriseTools(db_session)

    result = tools.get_supplier("Unknown Supplier")

    assert result is None


def test_search_purchase_orders_returns_only_delayed_orders(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE444444444",
        name="Purchase Order Tool Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    supplier.purchase_orders = [
        PurchaseOrder(
            order_number="PO-TOOL-001",
            status="delivered",
            ordered_at=date(2026, 8, 1),
            expected_delivery_date=date(2026, 8, 15),
            actual_delivery_date=date(2026, 8, 14),
            total_amount=Decimal("1000.00"),
        ),
        PurchaseOrder(
            order_number="PO-TOOL-002",
            status="delayed",
            ordered_at=date(2026, 8, 2),
            expected_delivery_date=date(2026, 8, 20),
            actual_delivery_date=None,
            total_amount=Decimal("2000.00"),
        ),
    ]

    db_session.add(supplier)
    db_session.flush()

    tools = EnterpriseTools(db_session)

    result = tools.search_purchase_orders(supplier.id)

    assert len(result) == 1

    purchase_order = result[0]

    assert purchase_order.purchase_order_id == supplier.purchase_orders[1].id
    assert purchase_order.order_number == "PO-TOOL-002"
    assert purchase_order.status == "delayed"
    assert purchase_order.ordered_at == date(2026, 8, 2)
    assert purchase_order.expected_delivery_date == date(2026, 8, 20)
    assert purchase_order.actual_delivery_date is None
    assert purchase_order.total_amount == Decimal("2000.00")


def test_search_service_tickets_returns_controlled_ticket_results(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE333333333",
        name="Ticket Tool Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    purchase_order = PurchaseOrder(
        order_number="PO-TOOL-TICKET-001",
        status="delayed",
        ordered_at=date(2026, 8, 1),
        expected_delivery_date=date(2026, 8, 15),
        actual_delivery_date=None,
        total_amount=Decimal("1500.00"),
    )

    supplier.purchase_orders = [purchase_order]

    supplier.service_tickets = [
        ServiceTicket(
            title="Supplier capacity issue",
            description="Supplier reports temporary production constraints.",
            status="open",
            priority="high",
            resolved_at=None,
        ),
        ServiceTicket(
            purchase_order=purchase_order,
            title="Order-specific quality issue",
            description="Material is awaiting quality inspection.",
            status="open",
            priority="medium",
            resolved_at=None,
        ),
    ]

    db_session.add(supplier)
    db_session.flush()

    tools = EnterpriseTools(db_session)

    result = tools.search_service_tickets(supplier.id)

    assert len(result) == 2

    supplier_ticket = next(
        ticket for ticket in result if ticket.purchase_order_id is None
    )
    purchase_order_ticket = next(
        ticket for ticket in result if ticket.purchase_order_id is not None
    )

    assert supplier_ticket.title == "Supplier capacity issue"
    assert supplier_ticket.status == "open"
    assert supplier_ticket.priority == "high"

    assert purchase_order_ticket.purchase_order_id == purchase_order.id
    assert purchase_order_ticket.title == "Order-specific quality issue"
    assert purchase_order_ticket.description == (
        "Material is awaiting quality inspection."
    )
