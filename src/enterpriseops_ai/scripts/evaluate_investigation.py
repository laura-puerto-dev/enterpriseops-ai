from pathlib import Path

from openai import OpenAI

from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.evaluation.investigation_judge import (
    InvestigationJudge,
    load_investigation_golden_dataset,
    run_and_evaluate_investigation_case,
)
from enterpriseops_ai.orchestration.factory import create_investigation_workflow


def main() -> None:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise RuntimeError(
            "OPENAI_API_KEY is required to run investigation evaluation."
        )

    cases = load_investigation_golden_dataset(
        Path("evals/investigation_golden_dataset.json")
    )

    client = OpenAI(api_key=settings.openai_api_key)
    judge = InvestigationJudge(client=client)

    with SessionFactory() as session:
        workflow = create_investigation_workflow(
            session=session,
            openai_api_key=settings.openai_api_key,
        )

        for case in cases:
            result = run_and_evaluate_investigation_case(
                case=case,
                workflow=workflow,
                judge=judge,
            )

            print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
