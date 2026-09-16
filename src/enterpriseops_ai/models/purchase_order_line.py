from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enterpriseops_ai.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from enterpriseops_ai.models.purchase_order import PurchaseOrder


class PurchaseOrderLine(TimestampMixin, Base):
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_order_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_orders.id"),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(
        back_populates="lines",
    )
