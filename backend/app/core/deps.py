"""Зависимости FastAPI (Depends)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Admin

from .database import async_session_factory, get_db
from .security import decode_session_token
from .settings import Settings, get_settings


# --- БД и настройки ---
get_db_dep = get_db
get_settings_dep = get_settings


# --- Администратор из сессии (cookie) ---
async def get_current_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """Возвращает текущего администратора по session cookie.

    Raises 401 если токен отсутствует, просрочен или админ не найден.
    """
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    settings = get_settings()
    max_age = settings.ADMIN_SESSION_MAX_AGE_HOURS * 3600
    payload = decode_session_token(token, max_age=max_age)
    if not payload or "admin_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия просрочена")

    from sqlalchemy import select

    result = await db.execute(select(Admin).where(Admin.id == payload["admin_id"]))
    admin = result.scalar_one_or_none()
    if admin is None or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Админ не найден")
    return admin


# --- Требование авторизации (для маршрутов) ---
require_admin = get_current_admin


# --- Шаблоны Jinja2 ---
_templates: Jinja2Templates | None = None


def get_templates() -> Jinja2Templates:
    """Возвращает Jinja2Templates (ленивая инициализация)."""
    global _templates
    if _templates is None:
        import pathlib

        tpl_dir = pathlib.Path(__file__).resolve().parent.parent / "templates"
        _templates = Jinja2Templates(directory=str(tpl_dir))
    return _templates
