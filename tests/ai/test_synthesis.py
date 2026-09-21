from unittest.mock import Mock

import pytest
from openai import OpenAI

from enterpriseops_ai.ai.synthesis import (
    InvestigationAnswer,
    SynthesisService,
)


def test_synthesize_returns_structured_answer() -> None:
    client = Mock(spec=OpenAI)

    expected_answer = InvestigationAnswer(
        summary="The available evidence is insufficient to determine the cause.",
        findings=[],
        evidence=[],
        sources=[],
        recommended_actions=["Collect purchase order and supplier incident data."],
        limitations=["No structured or documentary evidence was available."],
    )

    response = Mock()
    response.output_parsed = expected_answer
    client.responses.parse.return_value = response

    service = SynthesisService(client=client)

    result = service.synthesize(
        question="Why are ACME's orders late?",
        supplier=None,
        purchase_orders=[],
        service_tickets=[],
        documents=[],
        errors=[],
    )

    assert result == expected_answer
    client.responses.parse.assert_called_once()


def test_synthesize_fails_when_structured_answer_is_missing() -> None:
    client = Mock(spec=OpenAI)

    response = Mock()
    response.output_parsed = None
    client.responses.parse.return_value = response

    service = SynthesisService(client=client)

    with pytest.raises(
        RuntimeError,
        match="The LLM did not return a structured investigation answer.",
    ):
        service.synthesize(
            question="Why are ACME's orders late?",
            supplier=None,
            purchase_orders=[],
            service_tickets=[],
            documents=[],
            errors=[],
        )
