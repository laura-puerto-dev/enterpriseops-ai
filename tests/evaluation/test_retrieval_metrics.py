from enterpriseops_ai.evaluation.retrieval_metrics import (
    calculate_retrieval_metrics,
    reciprocal_rank,
)


def test_source_hit_at_first_position() -> None:
    metrics = calculate_retrieval_metrics(
        expected_sources=["supply_disruption_playbook.md"],
        retrieved_sources=[
            "supply_disruption_playbook.md",
            "supplier_delivery_policy.md",
        ],
    )

    assert metrics.source_hit is True
    assert metrics.first_relevant_rank == 1


def test_source_hit_at_later_position() -> None:
    metrics = calculate_retrieval_metrics(
        expected_sources=["supply_disruption_playbook.md"],
        retrieved_sources=[
            "quality_inspection_procedure.md",
            "supply_disruption_playbook.md",
        ],
    )

    assert metrics.source_hit is True
    assert metrics.first_relevant_rank == 2


def test_source_miss() -> None:
    metrics = calculate_retrieval_metrics(
        expected_sources=["supply_disruption_playbook.md"],
        retrieved_sources=[
            "quality_inspection_procedure.md",
            "supplier_delivery_policy.md",
        ],
    )

    assert metrics.source_hit is False
    assert metrics.first_relevant_rank is None


def test_no_expected_sources() -> None:
    metrics = calculate_retrieval_metrics(
        expected_sources=[],
        retrieved_sources=["supplier_delivery_policy.md"],
    )

    assert metrics.source_hit is False
    assert metrics.first_relevant_rank is None


def test_reciprocal_rank_at_first_position() -> None:
    assert reciprocal_rank(1) == 1.0


def test_reciprocal_rank_at_third_position() -> None:
    assert reciprocal_rank(3) == 1 / 3


def test_reciprocal_rank_when_no_relevant_result() -> None:
    assert reciprocal_rank(None) == 0.0
