"""Пользователь фонда, совместимый с fastapi-users."""

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """Краткое представление пользователя без данных для авторизации."""
        return (
            f'User(id={self.id!r}, '
            f'is_active={self.is_active!r}, '
            f'is_superuser={self.is_superuser!r})'
        )
