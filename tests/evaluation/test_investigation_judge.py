import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from enterpriseops_ai.ai.synthesis import InvestigationAnswer
from enterpriseops_ai.evaluation.investigation_judge import (
    InvestigationCriterionResult,
    InvestigationGoldenCase,
    InvestigationJudge,
    InvestigationJudgeResult,
    UnsupportedClaim,
    build_evaluation_result,
    calculate_coverage,
    evaluate_investigation_case,
    extract_investigation_evaluation_inputs,
    load_investigation_golden_dataset,
    run_and_evaluate_investigation_case,
    run_investigation_case,
)
from enterpriseops_ai.orchestration.state import (
    InvestigationState,
    create_initial_investigation_state,
)


def test_calculate_coverage_for_partial_support() -> None:
    criteria = [
        InvestigationCriterionResult(
            criterion="First criterion",
            supported=True,
            reason="Supported.",
        ),
        InvestigationCriterionResult(
            criterion="Second criterion",
            supported=True,
            reason="Supported.",
        ),
        InvestigationCriterionResult(
            criterion="Third criterion",
            supported=False,
            reason="Not supported.",
        ),
    ]

    assert calculate_coverage(criteria) == 2 / 3


def test_calculate_coverage_for_full_support() -> None:
    criteria = [
        InvestigationCriterionResult(
            criterion="First criterion",
            supported=True,
            reason="Supported.",
        ),
        InvestigationCriterionResult(
            criterion="Second criterion",
            supported=True,
            reason="Supported.",
        ),
    ]

    assert calculate_coverage(criteria) == 1.0


def test_calculate_coverage_with_no_criteria() -> None:
    assert calculate_coverage([]) == 0.0


def test_investigation_judge_returns_structured_result() -> None:
    expected_result = InvestigationJudgeResult(
        grounded=True,
        groundedness_reason="All factual claims are supported.",
        unsupported_claims=[],
        relevant=True,
        relevance_reason="The answer directly addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion="PO-002 is delayed due to capacity constraints.",
                supported=True,
                reason="The final answer states this cause.",
            ),
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion="No revised delivery date is available.",
                supported=True,
                reason="The final answer acknowledges this limitation.",
            ),
        ],
    )

    mock_client = MagicMock()
    mock_client.responses.parse.return_value.output_parsed = expected_result

    judge = InvestigationJudge(client=mock_client)

    result = judge.evaluate(
        question="Why are ACME purchase orders delayed?",
        expected_evidence=[
            "PO-002 is delayed due to capacity constraints.",
        ],
        expected_limitations=[
            "No revised delivery date is available.",
        ],
        available_evidence={
            "purchase_orders": [
                {
                    "po_number": "PO-002",
                    "status": "delayed",
                    "cause": "capacity constraints",
                }
            ]
        },
        final_answer=(
            "PO-002 is delayed due to capacity constraints. "
            "No revised delivery date is currently available."
        ),
    )

    assert result == expected_result
    mock_client.responses.parse.assert_called_once()


def test_investigation_judge_fails_when_structured_result_is_missing() -> None:
    mock_client = MagicMock()
    mock_client.responses.parse.return_value.output_parsed = None

    judge = InvestigationJudge(client=mock_client)

    with pytest.raises(
        RuntimeError,
        match="Investigation judge did not return a structured result.",
    ):
        judge.evaluate(
            question="Why are ACME purchase orders delayed?",
            expected_evidence=[
                "PO-002 is delayed due to capacity constraints.",
            ],
            expected_limitations=[
                "No revised delivery date is available.",
            ],
            available_evidence={
                "purchase_orders": [
                    {
                        "po_number": "PO-002",
                        "status": "delayed",
                        "cause": "capacity constraints",
                    }
                ]
            },
            final_answer="PO-002 is delayed due to capacity constraints.",
        )


def test_investigation_judge_fails_when_evidence_criteria_do_not_match() -> None:
    expected_evidence = [
        "PO-002 is delayed due to capacity constraints.",
        "PO-003 is delayed due to quality inspection.",
    ]

    incomplete_result = InvestigationJudgeResult(
        grounded=True,
        groundedness_reason="The claims are supported.",
        unsupported_claims=[],
        relevant=True,
        relevance_reason="The answer addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion="PO-002 is delayed due to capacity constraints.",
                supported=True,
                reason="The final answer states this cause.",
            ),
            # The second evidence criterion is deliberately missing.
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion="No revised delivery date is available.",
                supported=True,
                reason="The final answer acknowledges this limitation.",
            ),
        ],
    )

    mock_client = MagicMock()
    mock_client.responses.parse.return_value.output_parsed = incomplete_result

    judge = InvestigationJudge(client=mock_client)

    with pytest.raises(
        RuntimeError,
        match=(
            "Investigation judge returned evidence criteria that do not match "
            "the expected evidence."
        ),
    ):
        judge.evaluate(
            question="Why are ACME purchase orders delayed?",
            expected_evidence=expected_evidence,
            expected_limitations=[
                "No revised delivery date is available.",
            ],
            available_evidence={
                "purchase_orders": [
                    {
                        "po_number": "PO-002",
                        "status": "delayed",
                        "cause": "capacity constraints",
                    }
                ]
            },
            final_answer="PO-002 is delayed due to capacity constraints.",
        )


def test_investigation_judge_fails_when_limitation_criteria_do_not_match() -> None:
    expected_limitations = [
        "No revised delivery date is available.",
        "The capacity incident does not establish the cause of every delayed order.",
    ]

    incomplete_result = InvestigationJudgeResult(
        grounded=True,
        groundedness_reason="The claims are supported.",
        unsupported_claims=[],
        relevant=True,
        relevance_reason="The answer addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion="PO-002 is delayed due to capacity constraints.",
                supported=True,
                reason="The final answer states this cause.",
            ),
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion="No revised delivery date is available.",
                supported=True,
                reason="The final answer acknowledges this limitation.",
            ),
            # The second limitation criterion is deliberately missing.
        ],
    )

    mock_client = MagicMock()
    mock_client.responses.parse.return_value.output_parsed = incomplete_result

    judge = InvestigationJudge(client=mock_client)

    with pytest.raises(
        RuntimeError,
        match=(
            "Investigation judge returned limitation criteria that do not match "
            "the expected limitations."
        ),
    ):
        judge.evaluate(
            question="Why are ACME purchase orders delayed?",
            expected_evidence=[
                "PO-002 is delayed due to capacity constraints.",
            ],
            available_evidence={
                "purchase_orders": [
                    {
                        "po_number": "PO-002",
                        "status": "delayed",
                        "cause": "capacity constraints",
                    }
                ]
            },
            expected_limitations=expected_limitations,
            final_answer="PO-002 is delayed due to capacity constraints.",
        )


def test_load_investigation_golden_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "investigation_golden_dataset.json"
    dataset_path.write_text(
        """
        [
          {
            "id": "test-case",
            "question": "Why is the order delayed?",
            "expected_evidence": ["The order is delayed due to capacity constraints."],
            "expected_limitations": ["No revised delivery date is available."]
          }
        ]
        """,
        encoding="utf-8",
    )

    cases = load_investigation_golden_dataset(dataset_path)

    assert len(cases) == 1
    assert cases[0].id == "test-case"
    assert cases[0].question == "Why is the order delayed?"
    assert cases[0].expected_evidence == [
        "The order is delayed due to capacity constraints."
    ]
    assert cases[0].expected_limitations == ["No revised delivery date is available."]


def test_build_evaluation_result() -> None:
    judge_result = InvestigationJudgeResult(
        grounded=False,
        groundedness_reason="One factual claim is unsupported.",
        unsupported_claims=[
            UnsupportedClaim(
                claim="The supplier has provided a revised delivery date.",
                reason="No revised delivery date is present in the available evidence.",
            )
        ],
        relevant=True,
        relevance_reason="The answer directly addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion="First evidence criterion",
                supported=True,
                reason="Supported.",
            ),
            InvestigationCriterionResult(
                criterion="Second evidence criterion",
                supported=False,
                reason="Not supported.",
            ),
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion="First limitation criterion",
                supported=True,
                reason="Recognized.",
            )
        ],
    )

    result = build_evaluation_result(
        case_id="test-case",
        judge_result=judge_result,
    )

    assert result.case_id == "test-case"
    assert result.grounded is False
    assert result.relevant is True
    assert result.evidence_coverage == 0.5
    assert result.limitation_coverage == 1.0
    assert result.unsupported_claims == judge_result.unsupported_claims


def test_evaluate_investigation_case() -> None:
    case = InvestigationGoldenCase(
        id="test-case",
        question="Why is the order delayed?",
        expected_evidence=[
            "The order is delayed due to capacity constraints.",
        ],
        expected_limitations=[
            "No revised delivery date is available.",
        ],
    )

    judge_result = InvestigationJudgeResult(
        grounded=True,
        groundedness_reason="All factual claims are supported.",
        unsupported_claims=[],
        relevant=True,
        relevance_reason="The answer directly addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion="The order is delayed due to capacity constraints.",
                supported=True,
                reason="The answer states this cause.",
            )
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion="No revised delivery date is available.",
                supported=True,
                reason="The answer acknowledges this limitation.",
            )
        ],
    )

    judge = MagicMock()
    judge.evaluate.return_value = judge_result

    available_evidence: dict[str, object] = {
        "purchase_orders": [
            {
                "status": "delayed",
                "cause": "capacity constraints",
            }
        ]
    }

    final_answer = (
        "The order is delayed due to capacity constraints. "
        "No revised delivery date is available."
    )

    result = evaluate_investigation_case(
        case=case,
        available_evidence=available_evidence,
        final_answer=final_answer,
        judge=judge,
    )

    judge.evaluate.assert_called_once_with(
        question=case.question,
        expected_evidence=case.expected_evidence,
        expected_limitations=case.expected_limitations,
        available_evidence=available_evidence,
        final_answer=final_answer,
    )

    assert result.case_id == "test-case"
    assert result.grounded is True
    assert result.relevant is True
    assert result.evidence_coverage == 1.0
    assert result.limitation_coverage == 1.0
    assert result.unsupported_claims == []


def test_extract_investigation_evaluation_inputs() -> None:
    answer = InvestigationAnswer(
        summary="The order is delayed.",
        findings=["The delay is caused by capacity constraints."],
        evidence=["PO-002 is delayed."],
        sources=["purchase_orders"],
        recommended_actions=["Contact the supplier."],
        limitations=["No revised delivery date is available."],
    )

    state: InvestigationState = {
        "question": "Why is the order delayed?",
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": answer,
        "errors": [],
    }

    available_evidence, final_answer = extract_investigation_evaluation_inputs(state)

    assert available_evidence == {
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "workflow_errors": [],
    }

    assert json.loads(final_answer) == answer.model_dump()


def test_extract_investigation_evaluation_inputs_fails_without_answer() -> None:
    state: InvestigationState = {
        "question": "Why is the order delayed?",
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": [],
    }

    with pytest.raises(
        RuntimeError,
        match="Investigation workflow did not produce an answer.",
    ):
        extract_investigation_evaluation_inputs(state)


def test_run_investigation_case() -> None:
    case = InvestigationGoldenCase(
        id="test-case",
        question="Why is the order delayed?",
        expected_evidence=[],
        expected_limitations=[],
    )

    final_state: InvestigationState = {
        "question": case.question,
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": None,
        "errors": [],
    }

    workflow = Mock()
    workflow.invoke.return_value = final_state

    result = run_investigation_case(
        case=case,
        workflow=workflow,
    )

    workflow.invoke.assert_called_once_with(
        create_initial_investigation_state(
            question=case.question,
        )
    )

    assert result == final_state


def test_run_and_evaluate_investigation_case() -> None:
    case = InvestigationGoldenCase(
        id="test-case",
        question="Why is the order delayed?",
        expected_evidence=[
            "The order is delayed due to capacity constraints.",
        ],
        expected_limitations=[
            "No revised delivery date is available.",
        ],
    )

    answer = InvestigationAnswer(
        summary="The order is delayed due to capacity constraints.",
        findings=["The order is delayed due to capacity constraints."],
        evidence=["The order is delayed."],
        sources=["purchase_orders"],
        recommended_actions=["Contact the supplier."],
        limitations=["No revised delivery date is available."],
    )

    final_state: InvestigationState = {
        "question": case.question,
        "supplier_name": None,
        "supplier": None,
        "purchase_orders": [],
        "service_tickets": [],
        "documents": [],
        "answer": answer,
        "errors": [],
    }

    workflow = Mock()
    workflow.invoke.return_value = final_state

    judge_result = InvestigationJudgeResult(
        grounded=True,
        groundedness_reason="All factual claims are supported.",
        unsupported_claims=[],
        relevant=True,
        relevance_reason="The answer directly addresses the question.",
        evidence_criteria=[
            InvestigationCriterionResult(
                criterion=case.expected_evidence[0],
                supported=True,
                reason="The answer includes the expected evidence.",
            )
        ],
        limitation_criteria=[
            InvestigationCriterionResult(
                criterion=case.expected_limitations[0],
                supported=True,
                reason="The answer acknowledges the limitation.",
            )
        ],
    )

    judge = MagicMock()
    judge.evaluate.return_value = judge_result

    result = run_and_evaluate_investigation_case(
        case=case,
        workflow=workflow,
        judge=judge,
    )

    assert result.case_id == "test-case"
    assert result.grounded is True
    assert result.relevant is True
    assert result.evidence_coverage == 1.0
    assert result.limitation_coverage == 1.0
    assert result.unsupported_claims == []
