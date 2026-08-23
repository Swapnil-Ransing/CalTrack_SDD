"""Live-DB test: requires a reachable Postgres via DATABASE_URL.

Locally: `docker compose up -d` (see docker-compose.yml). In CI: the postgres service
container defined in .github/workflows/ci.yml.
"""

from __future__ import annotations

from sqlalchemy import text

from core.db import get_session


def test_can_connect_and_query() -> None:
    session = get_session()
    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close()
