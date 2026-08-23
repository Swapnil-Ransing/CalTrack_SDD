from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from models.user import ActivityLevel, Goal, Sex, User  # noqa: E402

__all__ = ["Base", "User", "Sex", "ActivityLevel", "Goal"]
