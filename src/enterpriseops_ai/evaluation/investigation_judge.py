import json

from openai import OpenAI
from pydantic import BaseModel


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


def calculate_coverage(
    criteria: list[InvestigationCriterionResult],
) -> float:
    if not criteria:
        return 0.0

    return sum(item.supported for item in criteria) / len(criteria)


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
