from pydantic import BaseModel

from enterpriseops_ai.ai.synthesis import InvestigationAnswer


class InvestigationRequest(BaseModel):
    question: str


class InvestigationResponse(BaseModel):
    answer: InvestigationAnswer | None
    errors: list[str]
