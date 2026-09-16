from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enterpriseops_ai.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from enterpriseops_ai.models.purchase_order import PurchaseOrder
    from enterpriseops_ai.models.supplier import Supplier


class ServiceTicket(TimestampMixin, Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    purchase_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("purchase_orders.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    supplier: Mapped["Supplier"] = relationship(
        back_populates="service_tickets",
    )
    purchase_order: Mapped["PurchaseOrder | None"] = relationship(
        back_populates="service_tickets",
    )
