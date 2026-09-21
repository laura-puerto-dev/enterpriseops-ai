from sqlalchemy.orm import Session

from enterpriseops_ai.models import Supplier, SupplierAlias
from enterpriseops_ai.repositories.supplier import SupplierRepository


def test_get_by_tax_id_returns_supplier_when_it_exists(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE999999999",
        name="Test Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    db_session.add(supplier)
    db_session.flush()

    repository = SupplierRepository(db_session)

    result = repository.get_by_tax_id("DE999999999")

    assert result is not None
    assert result.id == supplier.id
    assert result.tax_id == "DE999999999"
    assert result.name == "Test Supplier"


def test_get_by_tax_id_returns_none_when_supplier_does_not_exist(
    db_session: Session,
) -> None:
    repository = SupplierRepository(db_session)

    result = repository.get_by_tax_id("DE000000000")

    assert result is None


def test_get_by_name_returns_supplier_case_insensitively(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE888888888",
        name="Test Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    db_session.add(supplier)
    db_session.flush()

    repository = SupplierRepository(db_session)

    result = repository.get_by_name("  test supplier  ")

    assert result is not None
    assert result.id == supplier.id
    assert result.tax_id == "DE888888888"
    assert result.name == "Test Supplier"


def test_get_by_name_returns_none_when_supplier_does_not_exist(
    db_session: Session,
) -> None:
    repository = SupplierRepository(db_session)

    result = repository.get_by_name("Unknown Supplier")

    assert result is None


def test_resolve_by_name_or_alias_returns_supplier_by_canonical_name(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE777777777",
        name="Canonical Supplier",
        status="active",
        country="DE",
        lead_time_days=10,
    )
    db_session.add(supplier)
    db_session.flush()

    repository = SupplierRepository(db_session)

    result = repository.resolve_by_name_or_alias("Canonical Supplier")

    assert result is not None
    assert result.id == supplier.id


def test_resolve_by_name_or_alias_returns_supplier_by_alias(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE666666666",
        name="ACME Industrial Components",
        status="active",
        country="DE",
        lead_time_days=14,
    )
    supplier.aliases.append(SupplierAlias(alias="ACME"))

    db_session.add(supplier)
    db_session.flush()

    repository = SupplierRepository(db_session)

    result = repository.resolve_by_name_or_alias("ACME")

    assert result is not None
    assert result.id == supplier.id
    assert result.name == "ACME Industrial Components"


def test_resolve_by_name_or_alias_matches_alias_case_insensitively(
    db_session: Session,
) -> None:
    supplier = Supplier(
        tax_id="DE555555555",
        name="ACME Industrial Components",
        status="active",
        country="DE",
        lead_time_days=14,
    )
    supplier.aliases.append(SupplierAlias(alias="ACME"))

    db_session.add(supplier)
    db_session.flush()

    repository = SupplierRepository(db_session)

    result = repository.resolve_by_name_or_alias("  acme  ")

    assert result is not None
    assert result.id == supplier.id


def test_resolve_by_name_or_alias_returns_none_when_supplier_does_not_exist(
    db_session: Session,
) -> None:
    repository = SupplierRepository(db_session)

    result = repository.resolve_by_name_or_alias("Unknown Supplier")

    assert result is None
