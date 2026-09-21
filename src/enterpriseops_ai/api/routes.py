from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from enterpriseops_ai.api.schemas import InvestigationRequest, InvestigationResponse
from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.orchestration.factory import create_investigation_workflow
from enterpriseops_ai.orchestration.state import create_initial_investigation_state
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow

router = APIRouter(prefix="/ai", tags=["ai"])


def get_session() -> Generator[Session, None, None]:
    with SessionFactory() as session:
        yield session


def get_investigation_workflow(
    session: Annotated[Session, Depends(get_session)],
) -> InvestigationWorkflow:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise HTTPException(
            status_code=503,
            detail="AI investigation service is not configured.",
        )

    return create_investigation_workflow(
        session=session,
        openai_api_key=settings.openai_api_key,
    )


@router.post("/investigate")
def investigate(
    request: InvestigationRequest,
    workflow: Annotated[
        InvestigationWorkflow,
        Depends(get_investigation_workflow),
    ],
) -> InvestigationResponse:
    initial_state = create_initial_investigation_state(
        question=request.question,
    )

    result = workflow.invoke(initial_state)

    return InvestigationResponse(
        answer=result["answer"],
        errors=result["errors"],
    )
