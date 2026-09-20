from sqlalchemy import func, select
from sqlalchemy.orm import Session

from enterpriseops_ai.models import Supplier


class SupplierRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_tax_id(self, tax_id: str) -> Supplier | None:
        statement = select(Supplier).where(Supplier.tax_id == tax_id)
        return self.session.scalar(statement)

    def get_by_name(self, name: str) -> Supplier | None:
        statement = select(Supplier).where(
            func.lower(Supplier.name) == name.strip().lower()
        )
        return self.session.scalar(statement)
