"""FastAPI-приложение: минимальный скелет."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import async_engine, get_db, init_db
from backend.app.core.settings import get_settings
from backend.app.services.content import ContentService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: инициализация движка, create_all в dev."""
    settings = get_settings()
    if settings.APP_ENV == "development":
        await init_db()
    yield
    await async_engine.dispose()


settings = get_settings()
db_dependency = Depends(get_db)
app = FastAPI(
    title="Кухни на заказ — API",
    description="Платформа подбора и визуализации кухонь",
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", settings.APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health check ---
@app.get("/api/health")
async def health() -> dict:
    """Проверка работоспособности API."""
    return {"status": "ok"}


@app.get("/api/site-content")
async def site_content(db: AsyncSession = db_dependency) -> dict:
    """Публичный контент для статического frontend.

    GitHub Pages uses local fallback content until this endpoint is available on
    the VPS. Secrets and admin-only fields are never exposed here.
    """
    service = ContentService(db, get_settings())
    content = await service.get_site_content()
    return content.model_dump(mode="json")


# --- Статика ---
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
