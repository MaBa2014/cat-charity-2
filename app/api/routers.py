"""Единая точка подключения роутеров приложения QRKot."""

from fastapi import APIRouter

from app.api.endpoints.charity_project import router as projects_router
from app.api.endpoints.donation import router as donations_router
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(donations_router)
api_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

# Удаление пользователей не входит в API QRKot. Оставляем остальные
# маршруты FastAPI Users без изменений, сохраняя поведение Postman-тестов.
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if 'DELETE' not in route.methods
]
api_router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)
