from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from enterpriseops_ai.repositories.purchase_order import PurchaseOrderRepository
from enterpriseops_ai.repositories.service_ticket import ServiceTicketRepository
from enterpriseops_ai.repositories.supplier import SupplierRepository


@dataclass(frozen=True)
class SupplierResult:
    supplier_id: int
    tax_id: str
    name: str
    status: str
    country: str
    lead_time_days: int


@dataclass(frozen=True)
class PurchaseOrderResult:
    purchase_order_id: int
    order_number: str
    status: str
    ordered_at: date
    expected_delivery_date: date
    actual_delivery_date: date | None
    total_amount: Decimal


@dataclass(frozen=True)
class ServiceTicketResult:
    ticket_id: int
    purchase_order_id: int | None
    title: str
    description: str
    status: str
    priority: str
    resolved_at: datetime | None


class EnterpriseTools:
    def __init__(self, session: Session) -> None:
        self.supplier_repository = SupplierRepository(session)
        self.purchase_order_repository = PurchaseOrderRepository(session)
        self.service_ticket_repository = ServiceTicketRepository(session)

    def get_supplier(self, name: str) -> SupplierResult | None:
        supplier = self.supplier_repository.get_by_name(name)

        if supplier is None:
            return None

        return SupplierResult(
            supplier_id=supplier.id,
            tax_id=supplier.tax_id,
            name=supplier.name,
            status=supplier.status,
            country=supplier.country,
            lead_time_days=supplier.lead_time_days,
        )

    def search_purchase_orders(
        self,
        supplier_id: int,
    ) -> list[PurchaseOrderResult]:
        purchase_orders = self.purchase_order_repository.get_delayed_by_supplier(
            supplier_id
        )

        return [
            PurchaseOrderResult(
                purchase_order_id=purchase_order.id,
                order_number=purchase_order.order_number,
                status=purchase_order.status,
                ordered_at=purchase_order.ordered_at,
                expected_delivery_date=purchase_order.expected_delivery_date,
                actual_delivery_date=purchase_order.actual_delivery_date,
                total_amount=purchase_order.total_amount,
            )
            for purchase_order in purchase_orders
        ]

    def search_service_tickets(
        self,
        supplier_id: int,
    ) -> list[ServiceTicketResult]:
        tickets = self.service_ticket_repository.get_by_supplier(supplier_id)

        return [
            ServiceTicketResult(
                ticket_id=ticket.id,
                purchase_order_id=ticket.purchase_order_id,
                title=ticket.title,
                description=ticket.description,
                status=ticket.status,
                priority=ticket.priority,
                resolved_at=ticket.resolved_at,
            )
            for ticket in tickets
        ]
