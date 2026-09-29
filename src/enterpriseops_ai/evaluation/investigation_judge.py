import json
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from enterpriseops_ai.ai.synthesis import build_investigation_evidence_context
from enterpriseops_ai.orchestration.state import (
    InvestigationState,
    create_initial_investigation_state,
)
from enterpriseops_ai.orchestration.workflow import InvestigationWorkflow


class InvestigationGoldenCase(BaseModel):
    id: str
    question: str
    expected_evidence: list[str]
    expected_limitations: list[str]


def load_investigation_golden_dataset(
    path: Path,
) -> list[InvestigationGoldenCase]:
    data = json.loads(path.read_text(encoding="utf-8"))

    return [InvestigationGoldenCase.model_validate(case) for case in data]


class InvestigationCriterionResult(BaseModel):
    criterion: str
    supported: bool
    reason: str


class UnsupportedClaim(BaseModel):
    claim: str
    reason: str


class InvestigationJudgeResult(BaseModel):
    grounded: bool
    groundedness_reason: str
    unsupported_claims: list[UnsupportedClaim]

    relevant: bool
    relevance_reason: str

    evidence_criteria: list[InvestigationCriterionResult]
    limitation_criteria: list[InvestigationCriterionResult]


class InvestigationEvaluationResult(BaseModel):
    case_id: str
    grounded: bool
    relevant: bool
    evidence_coverage: float
    limitation_coverage: float
    unsupported_claims: list[UnsupportedClaim]


def calculate_coverage(
    criteria: list[InvestigationCriterionResult],
) -> float:
    if not criteria:
        return 0.0

    return sum(item.supported for item in criteria) / len(criteria)


def build_evaluation_result(
    case_id: str,
    judge_result: InvestigationJudgeResult,
) -> InvestigationEvaluationResult:
    return InvestigationEvaluationResult(
        case_id=case_id,
        grounded=judge_result.grounded,
        relevant=judge_result.relevant,
        evidence_coverage=calculate_coverage(judge_result.evidence_criteria),
        limitation_coverage=calculate_coverage(judge_result.limitation_criteria),
        unsupported_claims=judge_result.unsupported_claims,
    )


class InvestigationJudge:
    MODEL = "gpt-5-mini"

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def evaluate(
        self,
        question: str,
        expected_evidence: list[str],
        expected_limitations: list[str],
        available_evidence: dict[str, object],
        final_answer: str,
    ) -> InvestigationJudgeResult:
        evidence = "\n".join(
            f"{index}. {criterion}"
            for index, criterion in enumerate(expected_evidence, start=1)
        )

        limitations = "\n".join(
            f"{index}. {criterion}"
            for index, criterion in enumerate(expected_limitations, start=1)
        )

        available_evidence_json = json.dumps(
            available_evidence,
            default=str,
            indent=2,
        )

        response = self._client.responses.parse(
            model=self.MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative evaluator of enterprise AI investigations. "
                        "Evaluate the final answer using only the available investigation "
                        "evidence, expected evidence, and expected limitations supplied. "
                        "Do not use external knowledge. "
                        "Do not infer unsupported facts. "
                        "\n\n"
                        "Groundedness: determine whether the factual claims in the final "
                        "answer are supported by the available investigation evidence. "
                        "List every unsupported factual claim in unsupported_claims. "
                        "Set grounded to true only when there are no unsupported factual "
                        "claims. "
                        "\n\n"
                        "Relevance: determine whether the final answer directly addresses "
                        "the question. "
                        "\n\n"
                        "Evidence coverage: evaluate every expected evidence criterion "
                        "individually. Mark it supported only when the final answer "
                        "communicates that evidence correctly. "
                        "\n\n"
                        "Limitation recognition: evaluate every expected limitation "
                        "individually. Mark it supported only when the final answer "
                        "recognizes that limitation and does not contradict it. "
                        "\n\n"
                        "For both evidence_criteria and limitation_criteria, return exactly "
                        "one result for every supplied criterion. The criterion field must "
                        "contain only the original criterion text, copied verbatim and in "
                        "the same order. Do not include numeric prefixes, bullets, or "
                        "additional formatting."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        "Available investigation evidence:\n"
                        f"{available_evidence_json}\n\n"
                        f"Expected evidence:\n{evidence}\n\n"
                        f"Expected limitations:\n{limitations}\n\n"
                        f"Final answer:\n{final_answer}"
                    ),
                },
            ],
            text_format=InvestigationJudgeResult,
        )

        result = response.output_parsed

        if result is None:
            raise RuntimeError(
                "Investigation judge did not return a structured result."
            )

        returned_evidence = [
            criterion.criterion for criterion in result.evidence_criteria
        ]
        returned_limitations = [
            criterion.criterion for criterion in result.limitation_criteria
        ]

        if returned_evidence != expected_evidence:
            raise RuntimeError(
                "Investigation judge returned evidence criteria that do not match "
                "the expected evidence. "
                f"Expected: {expected_evidence!r}. "
                f"Returned: {returned_evidence!r}."
            )

        if returned_limitations != expected_limitations:
            raise RuntimeError(
                "Investigation judge returned limitation criteria that do not match "
                "the expected limitations. "
                f"Expected: {expected_limitations!r}. "
                f"Returned: {returned_limitations!r}."
            )

        return result


def evaluate_investigation_case(
    case: InvestigationGoldenCase,
    available_evidence: dict[str, object],
    final_answer: str,
    judge: InvestigationJudge,
) -> InvestigationEvaluationResult:
    judge_result = judge.evaluate(
        question=case.question,
        expected_evidence=case.expected_evidence,
        expected_limitations=case.expected_limitations,
        available_evidence=available_evidence,
        final_answer=final_answer,
    )

    return build_evaluation_result(
        case_id=case.id,
        judge_result=judge_result,
    )


def extract_investigation_evaluation_inputs(
    state: InvestigationState,
) -> tuple[dict[str, object], str]:
    answer = state["answer"]

    if answer is None:
        raise RuntimeError("Investigation workflow did not produce an answer.")

    available_evidence = build_investigation_evidence_context(
        supplier=state["supplier"],
        purchase_orders=state["purchase_orders"],
        service_tickets=state["service_tickets"],
        documents=state["documents"],
        errors=state["errors"],
    )

    final_answer = answer.model_dump_json(indent=2)

    return available_evidence, final_answer


def run_investigation_case(
    case: InvestigationGoldenCase,
    workflow: InvestigationWorkflow,
) -> InvestigationState:
    initial_state = create_initial_investigation_state(
        question=case.question,
    )

    return workflow.invoke(initial_state)
