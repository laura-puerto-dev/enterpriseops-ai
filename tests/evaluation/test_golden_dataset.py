import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from enterpriseops_ai.evaluation.golden_dataset import (
    Answerability,
    load_golden_dataset,
)


def test_load_golden_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "golden_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": "component-shortage-actions",
                    "question": "What should procurement do when a supplier reports a component shortage?",
                    "answerability": "ANSWERABLE",
                    "expected_sources": ["supply_disruption_playbook.md"],
                    "expected_evidence": ["identify affected purchase orders"],
                }
            ]
        ),
        encoding="utf-8",
    )

    cases = load_golden_dataset(dataset_path)

    assert len(cases) == 1
    assert cases[0].id == "component-shortage-actions"
    assert cases[0].answerability is Answerability.ANSWERABLE
    assert cases[0].expected_sources == ["supply_disruption_playbook.md"]
    assert cases[0].missing_evidence == []


def test_rejects_invalid_answerability(tmp_path: Path) -> None:
    dataset_path = tmp_path / "golden_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": "invalid-case",
                    "question": "Some question",
                    "answerability": "MAYBE",
                    "expected_sources": [],
                    "expected_evidence": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_golden_dataset(dataset_path)
