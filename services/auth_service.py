"""Password hashing and signed session tokens (phase 02)."""

from __future__ import annotations

from uuid import UUID

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from core.config import get_settings

SESSION_TOKEN_MAX_AGE_SECONDS = 30 * 24 * 60 * 60  # 30 days
_SESSION_SALT = "healthtracker-session"


def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().auth_secret_key, salt=_SESSION_SALT)


def create_session_token(user_id: UUID) -> str:
    return _serializer().dumps({"uid": str(user_id)})


def verify_session_token(token: str) -> UUID | None:
    try:
        data = _serializer().loads(token, max_age=SESSION_TOKEN_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    try:
        return UUID(data["uid"])
    except (KeyError, ValueError, TypeError):
        return None
