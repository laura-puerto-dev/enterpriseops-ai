from pathlib import Path
from statistics import mean

from enterpriseops_ai.core.config import get_settings
from enterpriseops_ai.db.session import SessionFactory
from enterpriseops_ai.evaluation.evidence_judge import (
    EvidenceJudge,
    calculate_evidence_coverage,
)
from enterpriseops_ai.evaluation.golden_dataset import (
    Answerability,
    load_golden_dataset,
)
from enterpriseops_ai.evaluation.retrieval_metrics import reciprocal_rank
from enterpriseops_ai.evaluation.retrieval_runner import RetrievalEvaluationRunner
from enterpriseops_ai.rag.embeddings import EmbeddingService
from enterpriseops_ai.repositories.document_chunk import DocumentChunkRepository


def main() -> None:
    top_k = 3

    settings = get_settings()

    if settings.openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is required to run retrieval evaluation.")

    cases = load_golden_dataset(Path("evals/golden_dataset.json"))

    with SessionFactory() as session:
        chunk_repository = DocumentChunkRepository(session)

        if chunk_repository.count() == 0:
            raise RuntimeError(
                "Cannot run retrieval evaluation: document corpus is empty."
            )

        runner = RetrievalEvaluationRunner(
            embedding_service=EmbeddingService(settings.openai_api_key),
            chunk_repository=chunk_repository,
            top_k=top_k,
        )

        results = [runner.evaluate_case(case) for case in cases]

        judge = EvidenceJudge(settings.openai_api_key)

        evidence_coverages: dict[str, float] = {}

        for case, result in zip(cases, results, strict=True):
            if not case.expected_evidence:
                continue

            judge_result = judge.evaluate(
                question=case.question,
                expected_evidence=case.expected_evidence,
                retrieved_context=result.retrieved_context,
            )

            evidence_coverages[case.id] = calculate_evidence_coverage(judge_result)

    for result in results:
        print(f"\n[{result.case_id}]")
        print(f"  answerability: {result.answerability}")
        print(f"  sources: {result.retrieved_sources}")
        print(f"  distances: {[round(distance, 4) for distance in result.distances]}")
        print(f"  source_hit@{top_k}: {result.metrics.source_hit}")
        print(f"  source_coverage@{top_k}: {result.metrics.source_coverage:.1%}")
        print(f"  first_relevant_rank: {result.metrics.first_relevant_rank}")
        if result.case_id in evidence_coverages:
            print(f"  evidence_coverage: {evidence_coverages[result.case_id]:.1%}")
        else:
            print("  evidence_coverage: N/A")
        print(f"  latency_ms: {result.latency_ms:.1f}")

    source_evaluable_results = [
        result
        for result in results
        if result.answerability != Answerability.UNANSWERABLE.value
    ]

    source_hit_rate = mean(
        result.metrics.source_hit for result in source_evaluable_results
    )

    mean_source_coverage = mean(
        result.metrics.source_coverage for result in source_evaluable_results
    )

    mean_reciprocal_rank = mean(
        reciprocal_rank(result.metrics.first_relevant_rank)
        for result in source_evaluable_results
    )

    mean_latency_ms = mean(result.latency_ms for result in results)

    mean_evidence_coverage = mean(evidence_coverages.values())

    print("\n=== Retrieval Evaluation Summary ===")
    print(f"Cases: {len(results)}")
    print(f"Source-evaluable cases: {len(source_evaluable_results)}")
    print(f"Source hit@{top_k}: {source_hit_rate:.1%}")
    print(f"Mean source coverage@{top_k}: {mean_source_coverage:.1%}")
    print(f"MRR: {mean_reciprocal_rank:.3f}")
    print(f"Mean latency: {mean_latency_ms:.1f} ms")
    print(f"Evidence-evaluable cases: {len(evidence_coverages)}")
    print(f"Mean evidence coverage: {mean_evidence_coverage:.1%}")


if __name__ == "__main__":
    main()
