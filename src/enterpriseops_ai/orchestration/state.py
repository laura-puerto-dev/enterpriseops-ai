from typing import TypedDict

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
    answer: str | None
    errors: list[str]


class InvestigationStateUpdate(TypedDict, total=False):
    question: str
    supplier_name: str | None
    supplier: SupplierResult | None
    purchase_orders: list[PurchaseOrderResult]
    service_tickets: list[ServiceTicketResult]
    documents: list[DocumentEvidence]
    answer: str | None
    errors: list[str]
