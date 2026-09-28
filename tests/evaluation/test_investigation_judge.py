from unittest.mock import MagicMock

import pytest

from enterpriseops_ai.evaluation.investigation_judge import (
    InvestigationCriterionResult,
    InvestigationJudge,
    InvestigationJudgeResult,
    calculate_coverage,
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
