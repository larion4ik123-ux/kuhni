"""Настройки (key/value) — редактируемые из админпанели.

Покрывает: telegram_bot_url, manager_chat_ids, ai_api_url, ai_model, max_url
(будущее), yandex_maps_url, yandex_widget_html, retention_days, consent_texts.
Секретные ключи (AI_API_KEY, TELEGRAM_BOT_TOKEN) — ТОЛЬКО в .env, не в БД.
"""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Setting(TimestampMixin, Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), default="general", nullable=False)
