from operator import add
from typing import Annotated, TypedDict

from enterpriseops_ai.ai.synthesis import InvestigationAnswer
from enterpriseops_ai.tools.documents import DocumentEvidence
from enterpriseops_ai.tools.enterprise import (
    PurchaseOrderResult,
    ServiceTicketResult,
    SupplierResult,
)


class InvestigationState(TypedDict):
    question: str
    supplier_name: str | None
    supplier: SupplierResult | None
    purchase_orders: list[PurchaseOrderResult]
    service_tickets: list[ServiceTicketResult]
    documents: list[DocumentEvidence]
    answer: InvestigationAnswer | None
    errors: Annotated[list[str], add]


class InvestigationStateUpdate(TypedDict, total=False):
    question: str
    supplier_name: str | None
    supplier: SupplierResult | None
    purchase_orders: list[PurchaseOrderResult]
    service_tickets: list[ServiceTicketResult]
    documents: list[DocumentEvidence]
    answer: InvestigationAnswer | None
    errors: list[str]


def create_initial_investigation_state(
    question: str,
) -> InvestigationState:
    return {
        "question": question,
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": [],
    }
