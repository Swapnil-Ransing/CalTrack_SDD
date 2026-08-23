"""Local test default: point DATABASE_URL at the Docker Compose Postgres unless the
environment (e.g. CI) already sets it."""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://healthtracker:healthtracker@localhost:5432/healthtracker",
)
