"""Настройки приложения. Читаем из .env через pydantic-settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.constants import AI_DEFAULT_MASTER_PROMPT


class Settings(BaseSettings):
    """Все настройки платформы кухонь. Секреты — только из .env."""

    # --- Приложение ---
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"

    # --- Безопасность ---
    SECRET_KEY: str = "change-me-in-production"
    CSRF_SECRET: str = "change-me-csrf"

    # --- База данных ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./data.db"

    # --- Администратор по умолчанию (seed) ---
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: str = "admin"
    ADMIN_SESSION_MAX_AGE_HOURS: int = 12

    # --- MAX (мессенджер) ---
    MAX_API_URL: str = "https://platform-api2.max.ru"
    MAX_BOT_TOKEN: str = ""
    MAX_BOT_URL: str = ""
    MAX_WEBHOOK_URL: str = ""
    MAX_WEBHOOK_SECRET: str = ""
    MAX_MANAGER_CHAT_IDS: list[int] = []

    # --- AI-провайдер ---
    AI_PROVIDER: str = "mock"  # mock | openai_compatible
    AI_API_BASE_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "bytedance/seedream-4.5"
    AI_QUALITY: str = "basic"
    AI_TIMEOUT: int = 600
    AI_RETRY_COUNT: int = 3
    AI_RESULTS_COUNT: int = 1
    AI_MASTER_PROMPT: str = AI_DEFAULT_MASTER_PROMPT

    # --- Медиа ---
    MEDIA_DIR: str = "./media"
    MEDIA_BASE_URL: str = "/media"
    MAX_UPLOAD_MB: int = 20

    # --- Хранение и очистка ---
    GENERATION_RETENTION_DAYS: int = 30
    BACKUP_DIR: str = "./backups"
    BACKUP_RETENTION_DAYS: int = 7

    # --- Rate limit ---
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("MAX_MANAGER_CHAT_IDS", mode="before")
    @classmethod
    def _parse_manager_chat_ids(cls, value):
        """MAX_MANAGER_CHAT_IDS may come as '123,456' from .env."""
        if isinstance(value, str):
            return [
                int(x.strip()) for x in value.split(",") if x.strip().lstrip("-").isdigit()
            ]
        return value


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""
    return Settings()
