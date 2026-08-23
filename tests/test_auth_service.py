"""Unit tests for services.auth_service — no DB, no Streamlit runtime needed."""

from __future__ import annotations

import uuid

import pytest

from services.auth_service import (
    create_session_token,
    hash_password,
    verify_password,
    verify_session_token,
)


def test_verify_password_accepts_correct_password() -> None:
    hashed = hash_password("correct-horse-battery-staple")

    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("correct-horse-battery-staple")

    assert verify_password("wrong-password", hashed) is False


def test_hash_password_salts_differently_each_time() -> None:
    first = hash_password("same-password")
    second = hash_password("same-password")

    assert first != second


def test_session_token_round_trips_to_the_right_user_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-key")
    user_id = uuid.uuid4()

    token = create_session_token(user_id)

    assert verify_session_token(token) == user_id


def test_tampered_session_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-key")
    token = create_session_token(uuid.uuid4())
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

    assert verify_session_token(tampered) is None


def test_expired_session_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-key")
    token = create_session_token(uuid.uuid4())

    import services.auth_service as auth_service

    original_max_age = auth_service.SESSION_TOKEN_MAX_AGE_SECONDS
    auth_service.SESSION_TOKEN_MAX_AGE_SECONDS = -1
    try:
        assert verify_session_token(token) is None
    finally:
        auth_service.SESSION_TOKEN_MAX_AGE_SECONDS = original_max_age


def test_session_token_with_wrong_secret_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pw@localhost:5432/db")
    monkeypatch.setenv("AUTH_SECRET_KEY", "secret-a")
    token = create_session_token(uuid.uuid4())

    monkeypatch.setenv("AUTH_SECRET_KEY", "secret-b")

    assert verify_session_token(token) is None
