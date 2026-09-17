from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from enterpriseops_ai.models import PurchaseOrder, Supplier
from enterpriseops_ai.repositories.purchase_order import PurchaseOrderRepository


def test_get_delayed_by_supplier_returns_only_delayed_orders(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE999999999",
        name="Test Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    supplier.purchase_orders = [
        PurchaseOrder(
            order_number="PO-TEST-001",
            status="delivered",
            ordered_at=date(2026, 8, 1),
            expected_delivery_date=date(2026, 8, 15),
            actual_delivery_date=date(2026, 8, 14),
            total_amount=Decimal("1000.00"),
        ),
        PurchaseOrder(
            order_number="PO-TEST-002",
            status="delayed",
            ordered_at=date(2026, 8, 2),
            expected_delivery_date=date(2026, 8, 20),
            actual_delivery_date=None,
            total_amount=Decimal("2000.00"),
        ),
        PurchaseOrder(
            order_number="PO-TEST-003",
            status="delayed",
            ordered_at=date(2026, 8, 3),
            expected_delivery_date=date(2026, 8, 18),
            actual_delivery_date=None,
            total_amount=Decimal("3000.00"),
        ),
    ]

    db_session.add(supplier)
    db_session.flush()

    repository = PurchaseOrderRepository(db_session)

    result = repository.get_delayed_by_supplier(supplier.id)

    assert [order.order_number for order in result] == [
        "PO-TEST-003",
        "PO-TEST-002",
    ]


def test_get_delayed_by_supplier_returns_empty_list_when_none_exist(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE888888888",
        name="Supplier Without Delays",
        status="active",
        country="DE",
        lead_time_days=10,
    )

    db_session.add(supplier)
    db_session.flush()

    repository = PurchaseOrderRepository(db_session)

    result = repository.get_delayed_by_supplier(supplier.id)

    assert result == []
