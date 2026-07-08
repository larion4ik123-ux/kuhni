"""Асинхронное подключение к БД (SQLAlchemy 2)."""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.models import Base

from .settings import get_settings


# --- Движок и фабрика сессий ---
_settings = get_settings()

_engine_kwargs: dict = {}
if _settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

async_engine = create_async_engine(
    _settings.DATABASE_URL,
    echo=_settings.APP_ENV == "development",
    future=True,
    **_engine_kwargs,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# --- События SQLite (WAL, FK) ---
@event.listens_for(async_engine.sync_engine, "connect")
def _on_connect(dbapi_conn, connection_record):
    """Включаем WAL, нормальную синхронизацию и foreign keys для SQLite."""
    if _settings.DATABASE_URL.startswith("sqlite"):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


# --- Зависимость FastAPI ---
async def get_db() -> AsyncSession:
    """Yield-сессия для FastAPI Depends."""
    async with async_session_factory() as session:
        yield session


# --- Инициализация (dev / тесты) ---
async def init_db(database_url: str | None = None) -> None:
    """Создаёт все таблицы (create_all). Использовать только в dev/тестах."""
    if database_url is not None:
        if not database_url.startswith("sqlite"):
            database_url = f"sqlite+aiosqlite:///{database_url}"
        engine = create_async_engine(database_url, future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
    else:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
