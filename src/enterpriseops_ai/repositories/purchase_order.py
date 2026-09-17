from sqlalchemy import select
from sqlalchemy.orm import Session

from enterpriseops_ai.models import PurchaseOrder


class PurchaseOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_delayed_by_supplier(self, supplier_id: int) -> list[PurchaseOrder]:
        statement = (
            select(PurchaseOrder)
            .where(
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.status == "delayed",
            )
            .order_by(PurchaseOrder.expected_delivery_date)
        )

        return list(self.session.scalars(statement))
