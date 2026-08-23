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
    auth_secret_key: str
    gemini_api_key: str | None = None


def _get_secret(key: str) -> str | None:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is None:
            # No live Streamlit session (Alembic, pytest, CI) — st.secrets would still
            # read straight off a developer's local secrets.toml on disk if present,
            # which isn't the "environment variables instead" fallback this resolver
            # promises for tooling contexts, so skip it and go to os.environ.
            return os.environ.get(key)

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
    auth_secret_key = _get_secret("AUTH_SECRET_KEY")
    if auth_secret_key is None:
        raise RuntimeError(
            "AUTH_SECRET_KEY is not set. Provide it via .streamlit/secrets.toml "
            "(local Streamlit runtime) or the AUTH_SECRET_KEY environment variable "
            "(Alembic, tests, CI)."
        )
    return Settings(
        database_url=database_url,
        auth_secret_key=auth_secret_key,
        gemini_api_key=_get_secret("GEMINI_API_KEY"),
    )
