import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Answerability(StrEnum):
    ANSWERABLE = "ANSWERABLE"
    PARTIALLY_ANSWERABLE = "PARTIALLY_ANSWERABLE"
    UNANSWERABLE = "UNANSWERABLE"


class GoldenDatasetCase(BaseModel):
    id: str
    question: str
    answerability: Answerability
    expected_sources: list[str]
    expected_evidence: list[str]
    missing_evidence: list[str] = Field(default_factory=list)


def load_golden_dataset(path: Path) -> list[GoldenDatasetCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [GoldenDatasetCase.model_validate(item) for item in data]
