"""Settings resolver that works both inside and outside a Streamlit runtime.

Inside `streamlit run`, values come from `st.secrets` (backed by
`.streamlit/secrets.toml`). Outside a Streamlit runtime — Alembic, pytest, CI — the same
keys are resolved from environment variables instead. Callers use `get_settings()` and
never touch `st.secrets` or `os.environ` directly.
"""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str
    gemini_api_key: str | None = None


def _get_secret(key: str) -> str | None:
    try:
        import streamlit as st

        value = st.secrets[key]
    except Exception:
        return os.environ.get(key)
    return str(value)


def get_settings() -> Settings:
    database_url = _get_secret("DATABASE_URL")
    if database_url is None:
        raise RuntimeError(
            "DATABASE_URL is not set. Provide it via .streamlit/secrets.toml "
            "(local Streamlit runtime) or the DATABASE_URL environment variable "
            "(Alembic, tests, CI)."
        )
    return Settings(
        database_url=database_url,
        gemini_api_key=_get_secret("GEMINI_API_KEY"),
    )
