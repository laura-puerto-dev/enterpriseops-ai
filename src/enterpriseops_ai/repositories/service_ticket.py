from sqlalchemy import select
from sqlalchemy.orm import Session

from enterpriseops_ai.models import ServiceTicket


class ServiceTicketRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_supplier(self, supplier_id: int) -> list[ServiceTicket]:
        statement = (
            select(ServiceTicket)
            .where(ServiceTicket.supplier_id == supplier_id)
            .order_by(ServiceTicket.created_at, ServiceTicket.id)
        )

        return list(self.session.scalars(statement))
