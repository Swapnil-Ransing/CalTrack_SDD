"""Unit tests for models.user — no DB needed, just metadata/mapping checks."""

from __future__ import annotations

from models import Base, User


def test_users_table_registered_on_base_metadata() -> None:
    assert "users" in Base.metadata.tables


def test_users_table_has_expected_columns() -> None:
    columns = Base.metadata.tables["users"].columns.keys()

    assert set(columns) == {
        "id",
        "email",
        "password_hash",
        "date_of_birth",
        "sex",
        "height_cm",
        "weight_kg",
        "activity_level",
        "goal",
        "created_at",
        "updated_at",
    }


def test_email_column_is_unique() -> None:
    email_column = Base.metadata.tables["users"].columns["email"]

    assert email_column.unique is True
    assert email_column.nullable is False


def test_user_mapped_class_importable() -> None:
    assert User.__tablename__ == "users"
