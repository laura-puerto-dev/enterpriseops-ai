from time import perf_counter

import structlog
from openai import OpenAI
from pydantic import BaseModel

logger = structlog.get_logger()


class InvestigationContext(BaseModel):
    supplier_name: str | None


class QuestionUnderstandingService:
    MODEL = "gpt-5-mini"

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def understand(self, question: str) -> InvestigationContext:
        start_time = perf_counter()
        response = self._client.responses.parse(
            model=self.MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Extract the supplier reference explicitly mentioned in the "
                        "user's investigation question. "
                        "Return only the supplier name or supplier reference itself, "
                        "without surrounding grammatical markers such as the possessive "
                        "'s. Preserve the supplier reference otherwise exactly as expressed "
                        "by the user. "
                        "Do not resolve, expand, correct, normalize, or guess the supplier "
                        "identity. "
                        'For example, if the user writes "ACME\'s late orders", return '
                        '"ACME", not "ACME\'s". '
                        "If no supplier is explicitly identifiable, return null."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            text_format=InvestigationContext,
        )

        usage = response.usage

        logger.info(
            "llm_call_completed",
            operation="question_understanding",
            model=self.MODEL,
            duration_ms=round((perf_counter() - start_time) * 1000, 2),
            input_tokens=usage.input_tokens if usage is not None else None,
            output_tokens=usage.output_tokens if usage is not None else None,
            total_tokens=usage.total_tokens if usage is not None else None,
        )

        result = response.output_parsed

        if result is None:
            raise RuntimeError(
                "Question understanding did not return a structured result."
            )

        return result
