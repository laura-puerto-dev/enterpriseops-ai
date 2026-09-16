from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from enterpriseops_ai.core.config import get_settings

settings = get_settings()

engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)
SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)
