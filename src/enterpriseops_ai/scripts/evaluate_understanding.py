from dataclasses import dataclass

from openai import OpenAI

from enterpriseops_ai.ai.understanding import QuestionUnderstandingService
from enterpriseops_ai.core.config import get_settings


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_supplier_name: str | None


CASES = [
    EvaluationCase(
        question="Investigate why purchase orders from supplier ACME are being delayed.",
        expected_supplier_name="ACME",
    ),
    EvaluationCase(
        question="What's going on with ACME's late orders?",
        expected_supplier_name="ACME",
    ),
    EvaluationCase(
        question="Investigate delivery problems from Global Industrial Parts.",
        expected_supplier_name="Global Industrial Parts",
    ),
    EvaluationCase(
        question="Why are purchase orders being delayed?",
        expected_supplier_name=None,
    ),
    EvaluationCase(
        question="Investigate ACME's recent delivery problems.",
        expected_supplier_name="ACME",
    ),
]


def main() -> None:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is required for understanding evaluation.")

    service = QuestionUnderstandingService(
        client=OpenAI(api_key=settings.openai_api_key)
    )

    passed = 0

    for case in CASES:
        result = service.understand(case.question)
        success = result.supplier_name == case.expected_supplier_name

        if success:
            passed += 1

        print(f"Question: {case.question}")
        print(f"Expected: {case.expected_supplier_name!r}")
        print(f"Actual:   {result.supplier_name!r}")
        print(f"Result:   {'PASS' if success else 'FAIL'}")
        print()

    print(f"Passed: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()
