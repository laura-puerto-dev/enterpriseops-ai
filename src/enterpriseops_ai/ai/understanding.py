from openai import OpenAI
from pydantic import BaseModel


class InvestigationContext(BaseModel):
    supplier_name: str | None


class QuestionUnderstandingService:
    MODEL = "gpt-5-mini"

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def understand(self, question: str) -> InvestigationContext:
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

        result = response.output_parsed

        if result is None:
            raise RuntimeError(
                "Question understanding did not return a structured result."
            )

        return result
