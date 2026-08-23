"""SQLAlchemy engine/session factory, built on top of core.config.get_settings()."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(get_settings().database_url)


def get_session() -> Session:
    session_factory = sessionmaker(bind=get_engine())
    return session_factory()
