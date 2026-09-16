from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enterpriseops_ai.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from enterpriseops_ai.models.purchase_order import PurchaseOrder
    from enterpriseops_ai.models.service_ticket import ServiceTicket


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(nullable=False)

    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(
        back_populates="supplier",
    )

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        back_populates="supplier",
    )
