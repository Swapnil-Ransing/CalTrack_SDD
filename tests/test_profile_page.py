"""AppTest coverage for pages/0_👤_Profile.py — gate, pre-fill, update.

Requires a reachable Postgres via DATABASE_URL (same live-DB pattern as
tests/test_db_connection.py). See the note in test_app_auth_flow.py about why each test
here starts from a directly-seeded session_state["user"] rather than a UI-driven login.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Iterator

import pytest
from sqlalchemy import delete
from streamlit.testing.v1 import AppTest

from core.db import get_session
from models.user import ActivityLevel, Goal, Sex, User
from schemas.user import UserSignup
from services.user_service import create_user

_PROFILE_PAGE = "../pages/0_👤_Profile.py"


@pytest.fixture
def cleanup_users() -> Iterator[list[str]]:
    created_emails: list[str] = []
    yield created_emails
    if created_emails:
        session = get_session()
        try:
            session.execute(delete(User).where(User.email.in_(created_emails)))
            session.commit()
        finally:
            session.close()


def _unique_email() -> str:
    return f"apptest-profile-{uuid.uuid4().hex}@example.com"


def _create_user_directly(email: str) -> User:
    session = get_session()
    try:
        user = create_user(
            session,
            UserSignup(
                email=email,
                password="supersecret",
                password_confirm="supersecret",
                date_of_birth=date(1990, 1, 1),
                sex=Sex.FEMALE,
                height_cm=165.0,
                weight_kg=60.0,
                activity_level=ActivityLevel.MODERATE,
                goal=Goal.MAINTAIN,
            ),
        )
        session.expunge(user)
        return user
    finally:
        session.close()


def test_auth_gate_stops_page_when_logged_out() -> None:
    at = AppTest.from_file(_PROFILE_PAGE)
    at.run(timeout=15)

    assert not at.exception
    assert len(at.text_input) == 0
    assert any("log in" in info.value.lower() for info in at.info)


def test_profile_page_prefills_current_values(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    user = _create_user_directly(email)

    at = AppTest.from_file(_PROFILE_PAGE)
    at.session_state["user"] = user
    at.run(timeout=15)

    assert not at.exception
    assert at.text_input[0].value == email
    assert at.date_input[0].value == date(1990, 1, 1)
    assert at.selectbox[0].value is Sex.FEMALE
    assert at.number_input[0].value == 165.0
    assert at.number_input[1].value == 60.0
    assert at.selectbox[1].value is ActivityLevel.MODERATE
    assert at.selectbox[2].value is Goal.MAINTAIN


def test_profile_update_succeeds_and_shows_confirmation(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    user = _create_user_directly(email)

    at = AppTest.from_file(_PROFILE_PAGE)
    at.session_state["user"] = user
    at.run(timeout=15)

    at.number_input[0].set_value(170.0)
    at.number_input[1].set_value(58.0)
    at.selectbox[2].set_value(Goal.LOSE_WEIGHT)
    at = at.button(key="FormSubmitter:profile_form-Save changes").click().run(timeout=15)

    assert not at.exception
    assert any("updated" in s.value.lower() for s in at.success)
    assert at.number_input[0].value == 170.0
    assert at.selectbox[2].value is Goal.LOSE_WEIGHT


def test_profile_update_rejects_conflicting_email(cleanup_users: list[str]) -> None:
    other_email = _unique_email()
    email = _unique_email()
    cleanup_users.extend([other_email, email])
    _create_user_directly(other_email)
    user = _create_user_directly(email)

    at = AppTest.from_file(_PROFILE_PAGE)
    at.session_state["user"] = user
    at.run(timeout=15)

    at.text_input[0].set_value(other_email)
    at = at.button(key="FormSubmitter:profile_form-Save changes").click().run(timeout=15)

    assert not at.exception
    assert any("already exists" in e.value for e in at.error)
