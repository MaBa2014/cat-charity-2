"""Настройки QRKot, включая URL базы по умолчанию для тестовой платформы."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'API для сбора и распределения пожертвований.'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'change-this-secret-in-your-production-environment'
    jwt_lifetime_seconds: int = 3600

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
