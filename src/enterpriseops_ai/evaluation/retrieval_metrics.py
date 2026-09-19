from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalMetrics:
    source_hit: bool
    source_coverage: float
    first_relevant_rank: int | None


def calculate_retrieval_metrics(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> RetrievalMetrics:
    if not expected_sources:
        return RetrievalMetrics(
            source_hit=False,
            source_coverage=0.0,
            first_relevant_rank=None,
        )

    expected = set(expected_sources)
    retrieved = set(retrieved_sources)

    matched_sources = expected & retrieved
    source_coverage = len(matched_sources) / len(expected)

    for rank, source in enumerate(retrieved_sources, start=1):
        if source in expected:
            return RetrievalMetrics(
                source_hit=True,
                source_coverage=source_coverage,
                first_relevant_rank=rank,
            )

    return RetrievalMetrics(
        source_hit=False,
        source_coverage=source_coverage,
        first_relevant_rank=None,
    )


def reciprocal_rank(first_relevant_rank: int | None) -> float:
    if first_relevant_rank is None:
        return 0.0

    return 1.0 / first_relevant_rank
