"""Unit tests for core.config.get_settings — no Streamlit runtime, no DB needed."""

from __future__ import annotations

import pytest

from core.config import get_settings


def test_get_settings_resolves_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://user:pw@localhost:5432/db"
    assert settings.gemini_api_key is None


def test_get_settings_resolves_optional_gemini_key_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    settings = get_settings()

    assert settings.gemini_api_key == "test-key"


def test_get_settings_raises_when_database_url_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError):
        get_settings()
