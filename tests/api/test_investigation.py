from fastapi.testclient import TestClient

from enterpriseops_ai.ai.synthesis import InvestigationAnswer
from enterpriseops_ai.api.routes import get_investigation_workflow
from enterpriseops_ai.main import app


class FakeInvestigationWorkflow:
    def invoke(self, state: object) -> dict[str, object]:
        return {
            "answer": InvestigationAnswer(
                summary="Supplier delays were identified.",
                findings=["Three purchase orders are delayed."],
                evidence=["Purchase order records show delayed status."],
                sources=["purchase_orders"],
                recommended_actions=["Review the delayed orders."],
                limitations=[],
            ),
            "errors": [],
        }


def override_investigation_workflow() -> FakeInvestigationWorkflow:
    return FakeInvestigationWorkflow()


def test_investigate_returns_structured_response() -> None:
    app.dependency_overrides[get_investigation_workflow] = (
        override_investigation_workflow
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/ai/investigate",
                json={
                    "question": (
                        "Why are purchase orders from supplier ACME being delayed?"
                    )
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "answer": {
                "summary": "Supplier delays were identified.",
                "findings": ["Three purchase orders are delayed."],
                "evidence": ["Purchase order records show delayed status."],
                "sources": ["purchase_orders"],
                "recommended_actions": ["Review the delayed orders."],
                "limitations": [],
            },
            "errors": [],
        }
    finally:
        app.dependency_overrides.clear()


def test_investigate_rejects_request_without_question() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/ai/investigate",
            json={},
        )

    assert response.status_code == 422
