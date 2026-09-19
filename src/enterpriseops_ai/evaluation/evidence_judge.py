from openai import OpenAI
from pydantic import BaseModel


class EvidenceCriterionResult(BaseModel):
    evidence: str
    supported: bool
    reason: str


class EvidenceJudgeResult(BaseModel):
    criteria: list[EvidenceCriterionResult]


def calculate_evidence_coverage(result: EvidenceJudgeResult) -> float:
    if not result.criteria:
        return 0.0

    supported_count = sum(criterion.supported for criterion in result.criteria)

    return supported_count / len(result.criteria)


class EvidenceJudge:
    MODEL = "gpt-5-mini"

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def evaluate(
        self,
        question: str,
        expected_evidence: list[str],
        retrieved_context: list[str],
    ) -> EvidenceJudgeResult:
        context = "\n\n".join(
            f"[Chunk {index}]\n{chunk}"
            for index, chunk in enumerate(retrieved_context, start=1)
        )

        criteria = "\n".join(
            f"{index}. {evidence}"
            for index, evidence in enumerate(expected_evidence, start=1)
        )

        response = self._client.responses.parse(
            model=self.MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative evidence evaluator. "
                        "Evaluate whether each expected evidence criterion is "
                        "supported by the retrieved context. "
                        "Use only the retrieved context. "
                        "Do not use external knowledge. "
                        "Do not infer unsupported facts. "
                        "Thematic similarity alone is not sufficient. "
                        "Mark a criterion as supported only when the context "
                        "provides sufficient evidence for it."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Expected evidence:\n{criteria}\n\n"
                        f"Retrieved context:\n{context}"
                    ),
                },
            ],
            text_format=EvidenceJudgeResult,
        )

        result = response.output_parsed

        if result is None:
            raise RuntimeError("Evidence judge did not return a structured result.")

        returned_evidence = [criterion.evidence for criterion in result.criteria]

        if returned_evidence != expected_evidence:
            raise RuntimeError(
                "Evidence judge returned criteria that do not match the expected evidence."
            )

        return result
