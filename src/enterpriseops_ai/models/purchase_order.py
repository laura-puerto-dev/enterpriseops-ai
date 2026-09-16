from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enterpriseops_ai.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from enterpriseops_ai.models.purchase_order_line import PurchaseOrderLine
    from enterpriseops_ai.models.service_ticket import ServiceTicket
    from enterpriseops_ai.models.supplier import Supplier


class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    ordered_at: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    supplier: Mapped["Supplier"] = relationship(
        back_populates="purchase_orders",
    )

    lines: Mapped[list["PurchaseOrderLine"]] = relationship(
        back_populates="purchase_order",
    )

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        back_populates="purchase_order",
    )
