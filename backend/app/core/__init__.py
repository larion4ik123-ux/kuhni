"""Core-модуль: настройки, БД, безопасность, зависимости."""

from __future__ import annotations

from .database import async_engine, async_session_factory, get_db, init_db
from .deps import get_current_admin, get_db_dep, get_settings_dep, get_templates, require_admin
from .security import (
    create_csrf_token,
    create_session_token,
    decode_session_token,
    hash_password,
    safe_filename,
    validate_csrf_token,
    verify_password,
)
from .settings import Settings, get_settings

__all__ = [
    "Settings",
    "async_engine",
    "async_session_factory",
    "create_csrf_token",
    "create_session_token",
    "decode_session_token",
    "get_current_admin",
    "get_db",
    "get_db_dep",
    "get_settings",
    "get_settings_dep",
    "get_templates",
    "hash_password",
    "init_db",
    "require_admin",
    "safe_filename",
    "validate_csrf_token",
    "verify_password",
]
