from sqlalchemy import func, select
from sqlalchemy.orm import Session

from enterpriseops_ai.models import Supplier, SupplierAlias


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

    def resolve_by_name_or_alias(self, name: str) -> Supplier | None:
        supplier = self.get_by_name(name)

        if supplier is not None:
            return supplier

        statement = (
            select(Supplier)
            .join(SupplierAlias)
            .where(func.lower(SupplierAlias.alias) == name.strip().lower())
        )
        return self.session.scalar(statement)
