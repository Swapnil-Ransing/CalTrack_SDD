"""Unit tests for core.auth — session_state caching and token delegation, with a stubbed
cookie manager (no real browser/component). Full login/logout/gate flow is covered by the
AppTest-based tests in test_app_auth_flow.py and test_profile_page.py.
"""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
import streamlit as st

import core.auth as auth_module
from models.user import ActivityLevel, Goal, Sex, User


@pytest.fixture(autouse=True)
def _clear_session_state() -> None:
    st.session_state.clear()


def _make_user() -> User:
    user = User(
        email="jane@example.com",
        password_hash="irrelevant",
        date_of_birth=date(1990, 1, 1),
        sex=Sex.FEMALE,
        height_cm=165.0,
        weight_kg=60.0,
        activity_level=ActivityLevel.MODERATE,
        goal=Goal.MAINTAIN,
    )
    user.id = uuid.uuid4()
    return user


def test_get_current_user_returns_cached_session_state_user_without_cookie_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _make_user()
    st.session_state["user"] = user
    stub_manager = MagicMock()
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)

    result = auth_module.get_current_user()

    assert result is user
    stub_manager.get_all.assert_not_called()


def test_get_current_user_returns_none_when_no_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_manager = MagicMock()
    stub_manager.get_all.return_value = {}
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)

    assert auth_module.get_current_user() is None


def test_get_current_user_returns_none_when_token_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_manager = MagicMock()
    stub_manager.get_all.return_value = {auth_module._COOKIE_NAME: "not-a-real-token"}
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)
    monkeypatch.setattr(auth_module, "verify_session_token", lambda token: None)

    assert auth_module.get_current_user() is None


def test_get_current_user_loads_and_caches_user_for_valid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _make_user()
    stub_manager = MagicMock()
    stub_manager.get_all.return_value = {auth_module._COOKIE_NAME: "valid-token"}
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)
    monkeypatch.setattr(auth_module, "verify_session_token", lambda token: user.id)
    monkeypatch.setattr(auth_module, "get_session", lambda: MagicMock())
    monkeypatch.setattr(
        auth_module.user_service, "get_user_by_id", lambda session, user_id: user
    )

    result = auth_module.get_current_user()

    assert result is user
    assert st.session_state["user"] is user


def test_get_current_user_returns_none_when_explicitly_logged_out_without_checking_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    st.session_state["_explicitly_logged_out"] = True
    stub_manager = MagicMock()
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)

    result = auth_module.get_current_user()

    assert result is None
    stub_manager.get_all.assert_not_called()


def test_login_user_sets_session_state_and_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    user = _make_user()
    stub_manager = MagicMock()
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)
    monkeypatch.setattr(auth_module, "create_session_token", lambda user_id: "a-token")

    auth_module.login_user(user)

    assert st.session_state["user"] is user
    assert st.session_state["_explicitly_logged_out"] is False
    stub_manager.set.assert_called_once()
    args, kwargs = stub_manager.set.call_args
    assert args[0] == auth_module._COOKIE_NAME
    assert args[1] == "a-token"
    assert kwargs["expires_at"] is not None


def test_logout_user_clears_session_state_and_deletes_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    st.session_state["user"] = _make_user()
    stub_manager = MagicMock()
    stub_manager.get_all.return_value = {auth_module._COOKIE_NAME: "some-token"}
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)

    auth_module.logout_user()

    assert st.session_state["user"] is None
    assert st.session_state["_explicitly_logged_out"] is True
    stub_manager.delete.assert_called_once_with(auth_module._COOKIE_NAME)


def test_logout_user_skips_delete_when_cookie_was_never_fetched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    st.session_state["user"] = _make_user()
    stub_manager = MagicMock()
    stub_manager.get_all.return_value = {}
    monkeypatch.setattr(auth_module, "_cookie_manager", lambda: stub_manager)

    auth_module.logout_user()

    assert st.session_state["user"] is None
    stub_manager.delete.assert_not_called()
