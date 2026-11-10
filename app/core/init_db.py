"""Создание суперпользователя для запуска Postman-коллекции."""

from sqlalchemy import select

from app.core.db import async_session_maker
from app.models import User  # noqa: F401 - registry всех таблиц
from fastapi_users.password import PasswordHelper


async def create_user(
    email: str, password: str, is_superuser: bool = False,
) -> None:
    """Создать учётную запись, если пользователь ещё не существует."""
    async with async_session_maker() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing is not None:
            return
        user = User(
            email=email,
            hashed_password=PasswordHelper().hash(password),
            is_active=True,
            is_verified=True,
            is_superuser=is_superuser,
        )
        session.add(user)
        await session.commit()
