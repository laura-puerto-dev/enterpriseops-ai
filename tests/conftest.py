from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from enterpriseops_ai.core.config import get_settings


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    settings = get_settings()

    test_database_url = (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/enterpriseops_test"
    )

    engine = create_engine(test_database_url)
    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

    connection = engine.connect()
    transaction = connection.begin()
    session = session_factory(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()
