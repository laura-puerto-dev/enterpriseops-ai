from datetime import date
from decimal import Decimal

from sqlalchemy import select

from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    ServiceTicket,
    Supplier,
)


def seed_database() -> None:
    with SessionFactory() as session:
        existing_supplier = session.scalar(
            select(Supplier).where(Supplier.name == "ACME Industrial Components")
        )

        if existing_supplier is not None:
            print("Seed data already exists.")
            return

        supplier = Supplier(
            tax_id="DE123456789",
            name="ACME Industrial Components",
            status="active",
            country="DE",
            lead_time_days=14,
        )

        po_001 = PurchaseOrder(
            order_number="PO-ACME-001",
            status="delivered",
            ordered_at=date(2026, 7, 1),
            expected_delivery_date=date(2026, 7, 15),
            actual_delivery_date=date(2026, 7, 14),
            total_amount=Decimal("12500.00"),
        )

        po_002 = PurchaseOrder(
            order_number="PO-ACME-002",
            status="delayed",
            ordered_at=date(2026, 8, 1),
            expected_delivery_date=date(2026, 8, 15),
            actual_delivery_date=None,
            total_amount=Decimal("18750.00"),
        )

        po_003 = PurchaseOrder(
            order_number="PO-ACME-003",
            status="delayed",
            ordered_at=date(2026, 8, 10),
            expected_delivery_date=date(2026, 8, 24),
            actual_delivery_date=None,
            total_amount=Decimal("9400.00"),
        )

        po_004 = PurchaseOrder(
            order_number="PO-ACME-004",
            status="delayed",
            ordered_at=date(2026, 8, 20),
            expected_delivery_date=date(2026, 9, 3),
            actual_delivery_date=None,
            total_amount=Decimal("22100.00"),
        )

        supplier.purchase_orders = [po_001, po_002, po_003, po_004]

        po_001.lines = [
            PurchaseOrderLine(
                product_code="VALVE-100",
                description="Industrial control valve",
                quantity=Decimal("25.00"),
            ),
        ]

        po_002.lines = [
            PurchaseOrderLine(
                product_code="PUMP-220",
                description="High-pressure industrial pump",
                quantity=Decimal("10.00"),
            ),
        ]

        po_003.lines = [
            PurchaseOrderLine(
                product_code="SENSOR-410",
                description="Temperature sensor",
                quantity=Decimal("40.00"),
            ),
        ]

        po_004.lines = [
            PurchaseOrderLine(
                product_code="ACTUATOR-330",
                description="Electric valve actuator",
                quantity=Decimal("15.00"),
            ),
        ]

        supplier.service_tickets = [
            ServiceTicket(
                title="Temporary production capacity constraints",
                description=(
                    "ACME reported temporary production capacity constraints "
                    "affecting current customer deliveries."
                ),
                status="open",
                priority="high",
                resolved_at=None,
            ),
            ServiceTicket(
                purchase_order=po_002,
                title="PO-ACME-002 affected by capacity constraints",
                description=(
                    "Delivery of PO-ACME-002 is delayed due to ACME's "
                    "temporary production capacity constraints."
                ),
                status="open",
                priority="high",
                resolved_at=None,
            ),
            ServiceTicket(
                purchase_order=po_003,
                title="Quality inspection blocking PO-ACME-003",
                description=(
                    "PO-ACME-003 is awaiting completion of an additional "
                    "quality inspection before shipment."
                ),
                status="open",
                priority="medium",
                resolved_at=None,
            ),
            ServiceTicket(
                purchase_order=po_004,
                title="Component shortage affecting PO-ACME-004",
                description=(
                    "PO-ACME-004 cannot be completed because a critical "
                    "component required for production is currently unavailable."
                ),
                status="open",
                priority="high",
                resolved_at=None,
            ),
        ]

        session.add(supplier)
        session.commit()

        print("Enterprise seed data created successfully.")


if __name__ == "__main__":
    seed_database()
