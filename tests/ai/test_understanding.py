from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from openai import OpenAI

from enterpriseops_ai.ai.understanding import (
    InvestigationContext,
    QuestionUnderstandingService,
)


def test_understand_returns_structured_context() -> None:
    client = Mock(spec=OpenAI)
    client.responses.parse.return_value = SimpleNamespace(
        output_parsed=InvestigationContext(supplier_name="ACME"),
        usage=None,
    )

    service = QuestionUnderstandingService(client=client)

    result = service.understand(
        "Investigate why purchase orders from supplier ACME are being delayed."
    )

    assert result == InvestigationContext(supplier_name="ACME")
    client.responses.parse.assert_called_once()


def test_understand_raises_when_structured_result_is_missing() -> None:
    client = Mock(spec=OpenAI)
    client.responses.parse.return_value = SimpleNamespace(
        output_parsed=None, usage=None
    )

    service = QuestionUnderstandingService(client=client)

    with pytest.raises(
        RuntimeError,
        match="Question understanding did not return a structured result.",
    ):
        service.understand("Investigate ACME.")
