"""Pydantic schemas for signup, login, and profile update/read (phase 02)."""

from __future__ import annotations

import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from models.user import ActivityLevel, Goal, Sex

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email_format(value: str) -> str:
    if not _EMAIL_PATTERN.match(value):
        raise ValueError("Enter a valid email address.")
    return value.lower()


class UserSignup(BaseModel):
    email: str
    password: str = Field(min_length=8)
    password_confirm: str
    date_of_birth: date
    sex: Sex
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    activity_level: ActivityLevel
    goal: Goal

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _validate_email_format(value)

    @model_validator(mode="after")
    def _check_passwords_match(self) -> "UserSignup":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _validate_email_format(value)


class UserProfileUpdate(BaseModel):
    email: str
    date_of_birth: date
    sex: Sex
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    activity_level: ActivityLevel
    goal: Goal

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _validate_email_format(value)


class UserOut(BaseModel):
    id: UUID
    email: str
    date_of_birth: date
    sex: Sex
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevel
    goal: Goal
    created_at: datetime

    model_config = {"from_attributes": True}
