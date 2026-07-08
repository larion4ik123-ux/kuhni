"""Безопасность: хеширование паролей, сессии, CSRF, имена файлов."""

from __future__ import annotations

import re
import secrets
from pathlib import Path

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .settings import get_settings


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет plain пароль против bcrypt-хеша."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8")[:72],
        hashed_password.encode("utf-8"),
    )


# --- Сессионные токены (cookie) ---
def _get_serializer() -> URLSafeTimedSerializer:
    """URLSafeTimedSerializer на SECRET_KEY."""
    return URLSafeTimedSerializer(get_settings().SECRET_KEY)


def create_session_token(data: dict) -> str:
    """Создаёт подписанный session token (cookie)."""
    return _get_serializer().dumps(data)


def decode_session_token(token: str, max_age: int | None = None) -> dict | None:
    """Декодирует и проверяет session token. Возвращает None при ошибке."""
    try:
        return _get_serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


# --- CSRF ---
def _get_csrf_serializer() -> URLSafeTimedSerializer:
    """URLSafeTimedSerializer на CSRF_SECRET."""
    return URLSafeTimedSerializer(get_settings().CSRF_SECRET)


def create_csrf_token() -> str:
    """Создаёт случайный CSRF-токен."""
    raw = secrets.token_urlsafe(32)
    return _get_csrf_serializer().dumps({"csrf": raw})


def validate_csrf_token(token: str, max_age: int = 3600) -> bool:
    """Проверяет CSRF-токен."""
    try:
        _get_csrf_serializer().loads(token, max_age=max_age)
        return True
    except (BadSignature, SignatureExpired):
        return False


# --- Имена файлов ---
def safe_filename(original: str) -> str:
    """Очищает имя файла от path-traversal и небезопасных символов.

    Возвращает безопасное имя (латиница, цифры, дефис, подчёркивание, точка).
    """
    name = Path(original).name
    stem = Path(name).stem
    suffix = Path(name).suffix.lower()
    clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_").lower()
    if not clean:
        clean = secrets.token_hex(8)
    return f"{clean}{suffix}"
