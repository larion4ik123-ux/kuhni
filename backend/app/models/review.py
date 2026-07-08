"""Отзывы.

Только реальные — source ('yandex'|'manual'|'widget') + source_url. Без
выдуманных данных. Если source_url пуст → отзыв скрыт (блок отзывов не
показывается, пока нет ни одного со ссылкой).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_name: Mapped[str] = mapped_column(String(128), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
