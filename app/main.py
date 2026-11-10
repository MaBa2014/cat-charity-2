"""ASGI-приложение фонда QRKot."""

from fastapi import FastAPI

from app.api.endpoints.charity_project import router as projects_router
from app.api.endpoints.donation import router as donations_router
from app.core.config import settings
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

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

app.include_router(projects_router)
app.include_router(donations_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
# В QRKot управление пользователями не предусматривает их удаление.
# FastAPI Users регистрирует DELETE /{id} по умолчанию, поэтому исключаем
# его до подключения роутера. Иначе Postman удаляет тестового пользователя,
# и последующие запросы с его JWT закономерно возвращают 401/404.
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if 'DELETE' not in route.methods
]
app.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)
