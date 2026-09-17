from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from enterpriseops_ai.models import PurchaseOrder, ServiceTicket, Supplier
from enterpriseops_ai.repositories.service_ticket import ServiceTicketRepository


def test_get_by_supplier_returns_supplier_and_purchase_order_tickets(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE777777777",
        name="Ticket Test Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    purchase_order = PurchaseOrder(
        order_number="PO-TICKET-001",
        status="delayed",
        ordered_at=date(2026, 8, 1),
        expected_delivery_date=date(2026, 8, 15),
        actual_delivery_date=None,
        total_amount=Decimal("1000.00"),
    )

    supplier.purchase_orders = [purchase_order]

    supplier.service_tickets = [
        ServiceTicket(
            title="Supplier-wide capacity issue",
            description="Temporary capacity constraints affect current deliveries.",
            status="open",
            priority="high",
            resolved_at=None,
        ),
        ServiceTicket(
            purchase_order=purchase_order,
            title="Purchase order quality issue",
            description="The purchase order is awaiting an additional quality inspection.",
            status="open",
            priority="medium",
            resolved_at=None,
        ),
    ]

    db_session.add(supplier)
    db_session.flush()

    repository = ServiceTicketRepository(db_session)

    result = repository.get_by_supplier(supplier.id)

    assert len(result) == 2

    supplier_wide_ticket = next(
        ticket for ticket in result if ticket.purchase_order_id is None
    )
    purchase_order_ticket = next(
        ticket for ticket in result if ticket.purchase_order_id is not None
    )

    assert supplier_wide_ticket.title == "Supplier-wide capacity issue"
    assert purchase_order_ticket.purchase_order_id == purchase_order.id
    assert purchase_order_ticket.title == "Purchase order quality issue"


def test_get_by_supplier_returns_empty_list_when_no_tickets_exist(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE666666666",
        name="Supplier Without Tickets",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    db_session.add(supplier)
    db_session.flush()

    repository = ServiceTicketRepository(db_session)

    result = repository.get_by_supplier(supplier.id)

    assert result == []
