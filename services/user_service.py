"""User account + profile persistence (phase 02)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserLogin, UserProfileUpdate, UserSignup
from services.auth_service import hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    """Raised when a signup or profile update would collide with another account's email."""


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.execute(
        select(User).where(User.email == email.lower())
    ).scalar_one_or_none()


def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)


def create_user(session: Session, data: UserSignup) -> User:
    if get_user_by_email(session, data.email) is not None:
        raise EmailAlreadyRegisteredError(f"{data.email} is already registered.")

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        date_of_birth=data.date_of_birth,
        sex=data.sex,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        activity_level=data.activity_level,
        goal=data.goal,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, data: UserLogin) -> User | None:
    user = get_user_by_email(session, data.email)
    if user is None:
        return None
    if not verify_password(data.password, user.password_hash):
        return None
    return user


def update_profile(session: Session, user_id: UUID, data: UserProfileUpdate) -> User:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise ValueError(f"No user with id {user_id}.")

    existing = get_user_by_email(session, data.email)
    if existing is not None and existing.id != user_id:
        raise EmailAlreadyRegisteredError(f"{data.email} is already registered.")

    user.email = data.email.lower()
    user.date_of_birth = data.date_of_birth
    user.sex = data.sex
    user.height_cm = data.height_cm
    user.weight_kg = data.weight_kg
    user.activity_level = data.activity_level
    user.goal = data.goal
    session.commit()
    session.refresh(user)
    return user
