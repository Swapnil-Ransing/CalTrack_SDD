"""AppTest coverage for the app.py auth gate: signup, login, logout.

Requires a reachable Postgres via DATABASE_URL (same live-DB pattern as
tests/test_db_connection.py) since signup/login exercise the real user_service against it.

Note on structure: streamlit.testing.v1.AppTest tracks widget state across the whole
element tree it has ever seen for a given AppTest instance, not just the current run's
tree. Chaining interactions that cross the auth-gate <-> home-screen boundary TWICE within
one AppTest instance (e.g. sign up, then click "Log out") trips a real AppTest limitation —
widgets that were part of an earlier run's tree but are absent from the current one raise a
KeyError deep in Streamlit's widget-state sync, not an error in our own code. Each test
below therefore does at most one such crossing: either it interacts purely within the
auth-gate (signup/login forms), or it starts from a directly-seeded `session_state["user"]`
(bypassing the auth-gate entirely, the same way get_current_user()'s session cache fast
path works in the real app) and only crosses into the auth-gate once, via logout.
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
    return f"apptest-{uuid.uuid4().hex}@example.com"


def _create_user_directly(email: str, password: str = "supersecret") -> User:
    session = get_session()
    try:
        user = create_user(
            session,
            UserSignup(
                email=email,
                password=password,
                password_confirm=password,
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


def _fill_signup_form(at: AppTest, email: str, password: str, confirm: str) -> AppTest:
    signup_tab = at.tabs[1]
    signup_tab.text_input[0].input(email)
    signup_tab.text_input[1].input(password)
    signup_tab.text_input[2].input(confirm)
    return signup_tab.button[0].click().run(timeout=15)


def test_signup_with_valid_data_logs_the_user_in(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    at = AppTest.from_file("../app.py")
    at.run(timeout=15)

    at = _fill_signup_form(at, email, "supersecret", "supersecret")

    assert not at.exception
    assert any(f"Welcome back, **{email}**" in md.value for md in at.markdown)


def test_signup_with_mismatched_passwords_shows_validation_error_and_stays_on_form(
    cleanup_users: list[str],
) -> None:
    email = _unique_email()
    at = AppTest.from_file("../app.py")
    at.run(timeout=15)

    at = _fill_signup_form(at, email, "supersecret", "different-password")

    assert not at.exception
    assert len(at.error) > 0
    assert not any("Welcome back" in md.value for md in at.markdown)


def test_login_with_wrong_password_shows_generic_error(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    _create_user_directly(email)

    at = AppTest.from_file("../app.py")
    at.run(timeout=15)
    login_tab = at.tabs[0]
    login_tab.text_input[0].input(email)
    login_tab.text_input[1].input("totally-wrong-password")
    at = login_tab.button[0].click().run(timeout=15)

    assert not at.exception
    assert any("Invalid email or password" in e.value for e in at.error)
    assert not any("Welcome back" in md.value for md in at.markdown)


def test_login_with_correct_password_logs_the_user_in(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    _create_user_directly(email)

    at = AppTest.from_file("../app.py")
    at.run(timeout=15)
    login_tab = at.tabs[0]
    login_tab.text_input[0].input(email)
    login_tab.text_input[1].input("supersecret")
    at = login_tab.button[0].click().run(timeout=15)

    assert not at.exception
    assert any(f"Welcome back, **{email}**" in md.value for md in at.markdown)


def test_logout_returns_to_the_auth_gate(cleanup_users: list[str]) -> None:
    email = _unique_email()
    cleanup_users.append(email)
    user = _create_user_directly(email)

    at = AppTest.from_file("../app.py")
    at.session_state["user"] = user
    at.run(timeout=15)
    assert any(f"Welcome back, **{email}**" in md.value for md in at.markdown)

    at = at.button(key="logout_button").click().run(timeout=15)

    assert not at.exception
    assert len(at.tabs) == 2
    assert not any("Welcome back" in md.value for md in at.markdown)


def test_unauthenticated_visit_shows_auth_gate_not_home(cleanup_users: list[str]) -> None:
    at = AppTest.from_file("../app.py")
    at.run(timeout=15)

    assert not at.exception
    assert len(at.tabs) == 2
    assert not any("Welcome back" in md.value for md in at.markdown)
