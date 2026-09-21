from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enterpriseops_ai.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from enterpriseops_ai.models.supplier import Supplier


class SupplierAlias(TimestampMixin, Base):
    __tablename__ = "supplier_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
    )
    alias: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    supplier: Mapped["Supplier"] = relationship(
        back_populates="aliases",
    )
