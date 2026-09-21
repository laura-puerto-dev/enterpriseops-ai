from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.orchestration.factory import create_investigation_workflow
from enterpriseops_ai.orchestration.state import (
    create_initial_investigation_state,
)


def main() -> None:
    settings = get_settings()

    if settings.openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is required to run an investigation.")

    with SessionFactory() as session:
        workflow = create_investigation_workflow(
            session=session,
            openai_api_key=settings.openai_api_key,
        )

        initial_state = create_initial_investigation_state(
            question="Why are purchase orders from supplier ACME being delayed?"
        )

        result = workflow.invoke(initial_state)

        print("\n=== INVESTIGATION RESULT ===\n")
        print(
            result["answer"].model_dump_json(indent=2)
            if result["answer"]
            else "No answer"
        )

        print("\n=== WORKFLOW ERRORS ===\n")
        print(result["errors"])


if __name__ == "__main__":
    main()
