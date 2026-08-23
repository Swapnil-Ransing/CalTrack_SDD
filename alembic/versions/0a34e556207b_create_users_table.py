"""create users table

Revision ID: 0a34e556207b
Revises:
Create Date: 2026-08-23 16:45:37.746510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0a34e556207b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

sex_enum = postgresql.ENUM("male", "female", "other", name="sex")
activity_level_enum = postgresql.ENUM(
    "sedentary", "light", "moderate", "active", "very_active", name="activity_level"
)
goal_enum = postgresql.ENUM("lose_weight", "maintain", "gain_weight", name="goal")

# Columns reference the already-created types below without re-issuing CREATE TYPE
# (op.create_table would otherwise try to create them again as part of the table DDL).
sex_column_type = postgresql.ENUM(
    "male", "female", "other", name="sex", create_type=False
)
activity_level_column_type = postgresql.ENUM(
    "sedentary",
    "light",
    "moderate",
    "active",
    "very_active",
    name="activity_level",
    create_type=False,
)
goal_column_type = postgresql.ENUM(
    "lose_weight", "maintain", "gain_weight", name="goal", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    bind = op.get_bind()
    sex_enum.create(bind, checkfirst=True)
    activity_level_enum.create(bind, checkfirst=True)
    goal_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("sex", sex_column_type, nullable=False),
        sa.Column("height_cm", sa.Numeric(5, 1), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 1), nullable=False),
        sa.Column("activity_level", activity_level_column_type, nullable=False),
        sa.Column("goal", goal_column_type, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    goal_enum.drop(op.get_bind(), checkfirst=True)
    activity_level_enum.drop(op.get_bind(), checkfirst=True)
    sex_enum.drop(op.get_bind(), checkfirst=True)
    # pgcrypto extension is left in place — other objects/dbs may depend on it.
