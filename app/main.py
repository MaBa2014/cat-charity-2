"""ASGI-приложение фонда QRKot."""

from fastapi import FastAPI

from app.api.routers import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0.0',
    openapi_tags=[
        {'name': 'charity_projects', 'description': 'Целевые сборы'},
        {'name': 'donations', 'description': 'Пожертвования'},
        {'name': 'auth', 'description': 'Регистрация и JWT-аутентификация'},
        {'name': 'users', 'description': 'Управление пользователями'},
    ],
)

app.include_router(api_router)
