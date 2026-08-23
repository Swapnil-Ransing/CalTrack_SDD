"""Unit tests for schemas.user — pure validation, no DB."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from models.user import ActivityLevel, Goal, Sex
from schemas.user import UserLogin, UserProfileUpdate, UserSignup

VALID_SIGNUP: dict[str, Any] = {
    "email": "Jane@Example.com",
    "password": "supersecret",
    "password_confirm": "supersecret",
    "date_of_birth": date(1990, 1, 1),
    "sex": Sex.FEMALE,
    "height_cm": 165.0,
    "weight_kg": 60.0,
    "activity_level": ActivityLevel.MODERATE,
    "goal": Goal.MAINTAIN,
}


def test_valid_signup_payload_passes_and_lowercases_email() -> None:
    signup = UserSignup(**VALID_SIGNUP)

    assert signup.email == "jane@example.com"


def test_signup_rejects_short_password() -> None:
    payload = {**VALID_SIGNUP, "password": "short1", "password_confirm": "short1"}

    with pytest.raises(ValidationError):
        UserSignup(**payload)


def test_signup_rejects_mismatched_password_confirmation() -> None:
    payload = {**VALID_SIGNUP, "password_confirm": "somethingelse"}

    with pytest.raises(ValidationError):
        UserSignup(**payload)


def test_signup_rejects_invalid_email_format() -> None:
    payload = {**VALID_SIGNUP, "email": "not-an-email"}

    with pytest.raises(ValidationError):
        UserSignup(**payload)


def test_login_rejects_invalid_email_format() -> None:
    with pytest.raises(ValidationError):
        UserLogin(email="not-an-email", password="whatever")


def test_login_accepts_valid_payload() -> None:
    login = UserLogin(email="Jane@Example.com", password="whatever")

    assert login.email == "jane@example.com"


def test_profile_update_rejects_invalid_email_format() -> None:
    payload = {k: v for k, v in VALID_SIGNUP.items() if k not in ("password", "password_confirm")}
    payload["email"] = "not-an-email"

    with pytest.raises(ValidationError):
        UserProfileUpdate(**payload)


def test_profile_update_accepts_valid_payload() -> None:
    payload = {k: v for k, v in VALID_SIGNUP.items() if k not in ("password", "password_confirm")}

    update = UserProfileUpdate(**payload)

    assert update.email == "jane@example.com"
    assert update.sex is Sex.FEMALE
