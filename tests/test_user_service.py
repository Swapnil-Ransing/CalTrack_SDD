"""Integration tests for services.user_service — requires a reachable Postgres via
DATABASE_URL (see tests/test_db_connection.py for the same live-DB pattern).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Iterator

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from core.db import get_session
from models.user import ActivityLevel, Goal, Sex, User
from schemas.user import UserLogin, UserProfileUpdate, UserSignup
from services.user_service import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_profile,
)


@pytest.fixture
def session() -> Iterator[Session]:
    db_session = get_session()
    created_emails: list[str] = []
    db_session.info["created_emails"] = created_emails
    try:
        yield db_session
    finally:
        if created_emails:
            db_session.execute(delete(User).where(User.email.in_(created_emails)))
            db_session.commit()
        db_session.close()


def _signup_payload(email: str) -> UserSignup:
    return UserSignup(
        email=email,
        password="supersecret",
        password_confirm="supersecret",
        date_of_birth=date(1990, 1, 1),
        sex=Sex.FEMALE,
        height_cm=165.0,
        weight_kg=60.0,
        activity_level=ActivityLevel.MODERATE,
        goal=Goal.MAINTAIN,
    )


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex}@example.com"


def test_create_user_succeeds_and_hashes_password(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)

    user = create_user(session, _signup_payload(email))

    assert user.id is not None
    assert user.email == email
    assert user.password_hash != "supersecret"


def test_create_user_rejects_duplicate_email(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    create_user(session, _signup_payload(email))

    with pytest.raises(EmailAlreadyRegisteredError):
        create_user(session, _signup_payload(email))


def test_authenticate_user_succeeds_with_correct_credentials(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    create_user(session, _signup_payload(email))

    user = authenticate_user(session, UserLogin(email=email, password="supersecret"))

    assert user is not None
    assert user.email == email


def test_authenticate_user_fails_with_wrong_password(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    create_user(session, _signup_payload(email))

    user = authenticate_user(session, UserLogin(email=email, password="wrong-password"))

    assert user is None


def test_authenticate_user_fails_with_unknown_email(session: Session) -> None:
    user = authenticate_user(
        session, UserLogin(email=_unique_email(), password="whatever1")
    )

    assert user is None


def test_get_user_by_id_returns_created_user(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    created = create_user(session, _signup_payload(email))

    fetched = get_user_by_id(session, created.id)

    assert fetched is not None
    assert fetched.email == email


def test_update_profile_succeeds(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    user = create_user(session, _signup_payload(email))

    updated = update_profile(
        session,
        user.id,
        UserProfileUpdate(
            email=email,
            date_of_birth=date(1991, 2, 2),
            sex=Sex.OTHER,
            height_cm=170.0,
            weight_kg=62.0,
            activity_level=ActivityLevel.ACTIVE,
            goal=Goal.LOSE_WEIGHT,
        ),
    )

    assert updated.height_cm == pytest.approx(170.0)
    assert updated.sex is Sex.OTHER
    assert updated.goal is Goal.LOSE_WEIGHT


def test_update_profile_rejects_conflicting_email(session: Session) -> None:
    email_a = _unique_email()
    email_b = _unique_email()
    session.info["created_emails"].extend([email_a, email_b])
    create_user(session, _signup_payload(email_a))
    user_b = create_user(session, _signup_payload(email_b))

    with pytest.raises(EmailAlreadyRegisteredError):
        update_profile(
            session,
            user_b.id,
            UserProfileUpdate(
                email=email_a,
                date_of_birth=date(1991, 2, 2),
                sex=Sex.OTHER,
                height_cm=170.0,
                weight_kg=62.0,
                activity_level=ActivityLevel.ACTIVE,
                goal=Goal.LOSE_WEIGHT,
            ),
        )


def test_update_profile_allows_keeping_same_email(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    user = create_user(session, _signup_payload(email))

    updated = update_profile(
        session,
        user.id,
        UserProfileUpdate(
            email=email,
            date_of_birth=date(1991, 2, 2),
            sex=Sex.MALE,
            height_cm=180.0,
            weight_kg=80.0,
            activity_level=ActivityLevel.SEDENTARY,
            goal=Goal.GAIN_WEIGHT,
        ),
    )

    assert updated.email == email


def test_get_user_by_email_is_case_insensitive(session: Session) -> None:
    email = _unique_email()
    session.info["created_emails"].append(email)
    create_user(session, _signup_payload(email))

    fetched = get_user_by_email(session, email.upper())

    assert fetched is not None
    assert fetched.email == email
