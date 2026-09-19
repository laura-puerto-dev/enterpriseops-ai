from unittest.mock import MagicMock, patch

import pytest

from enterpriseops_ai.evaluation.evidence_judge import (
    EvidenceCriterionResult,
    EvidenceJudge,
    EvidenceJudgeResult,
    calculate_evidence_coverage,
)


def test_calculate_evidence_coverage_for_partial_support() -> None:
    result = EvidenceJudgeResult(
        criteria=[
            EvidenceCriterionResult(
                criterion="Identify affected purchase orders",
                supported=True,
                reason="The context explicitly identifies affected purchase orders.",
            ),
            EvidenceCriterionResult(
                criterion="Identify unavailable component",
                supported=True,
                reason="The context identifies the unavailable component.",
            ),
            EvidenceCriterionResult(
                criterion="Obtain revised supplier commitment",
                supported=False,
                reason="No revised supplier commitment is present in the context.",
            ),
        ]
    )

    assert calculate_evidence_coverage(result) == 2 / 3


def test_calculate_evidence_coverage_for_full_support() -> None:
    result = EvidenceJudgeResult(
        criteria=[
            EvidenceCriterionResult(
                criterion="First criterion",
                supported=True,
                reason="Supported.",
            ),
            EvidenceCriterionResult(
                criterion="Second criterion",
                supported=True,
                reason="Supported.",
            ),
        ]
    )

    assert calculate_evidence_coverage(result) == 1.0


def test_calculate_evidence_coverage_with_no_criteria() -> None:
    result = EvidenceJudgeResult(criteria=[])

    assert calculate_evidence_coverage(result) == 0.0


@patch("enterpriseops_ai.evaluation.evidence_judge.OpenAI")
def test_evidence_judge_returns_structured_result(
    mock_openai: MagicMock,
) -> None:
    expected_result = EvidenceJudgeResult(
        criteria=[
            EvidenceCriterionResult(
                criterion="Identify affected purchase orders",
                supported=True,
                reason="The context explicitly identifies affected purchase orders.",
            ),
            EvidenceCriterionResult(
                criterion="Obtain revised supplier commitment",
                supported=False,
                reason="The context does not provide a revised supplier commitment.",
            ),
        ]
    )

    mock_client = mock_openai.return_value
    mock_client.responses.parse.return_value.output_parsed = expected_result

    judge = EvidenceJudge(api_key="test-key")

    result = judge.evaluate(
        question="What actions should be taken for a component shortage?",
        expected_evidence=[
            "Identify affected purchase orders",
            "Obtain revised supplier commitment",
        ],
        retrieved_context=[
            "Review the affected purchase orders.",
            "The supplier reported a component shortage.",
        ],
    )

    assert result == expected_result
    mock_client.responses.parse.assert_called_once()


@patch("enterpriseops_ai.evaluation.evidence_judge.OpenAI")
def test_evidence_judge_fails_when_structured_result_is_missing(
    mock_openai: MagicMock,
) -> None:
    mock_client = mock_openai.return_value
    mock_client.responses.parse.return_value.output_parsed = None

    judge = EvidenceJudge(api_key="test-key")

    with pytest.raises(
        RuntimeError,
        match="Evidence judge did not return a structured result.",
    ):
        judge.evaluate(
            question="What actions should be taken?",
            expected_evidence=["Identify affected purchase orders"],
            retrieved_context=["Review the affected purchase orders."],
        )


@patch("enterpriseops_ai.evaluation.evidence_judge.OpenAI")
def test_evidence_judge_fails_when_criteria_do_not_match(
    mock_openai: MagicMock,
) -> None:
    expected_evidence = [
        "Identify affected purchase orders",
        "Identify the unavailable component",
        "Obtain revised supplier commitment",
    ]

    incomplete_result = EvidenceJudgeResult(
        criteria=[
            EvidenceCriterionResult(
                criterion="Identify affected purchase orders",
                supported=True,
                reason="The context supports it.",
            ),
            EvidenceCriterionResult(
                criterion="Identify the unavailable component",
                supported=True,
                reason="The context supports it.",
            ),
            # The third criterion is deliberately missing.
        ]
    )

    mock_client = mock_openai.return_value
    mock_client.responses.parse.return_value.output_parsed = incomplete_result

    judge = EvidenceJudge(api_key="test-key")

    with pytest.raises(
        RuntimeError,
        match="Evidence judge returned criteria that do not match the expected evidence.",
    ):
        judge.evaluate(
            question="What actions should be taken for a component shortage?",
            expected_evidence=expected_evidence,
            retrieved_context=[
                "The supplier reported a component shortage affecting several purchase orders."
            ],
        )
