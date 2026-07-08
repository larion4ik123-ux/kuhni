"""Метаданные файла на диске.

Сами файлы — в MEDIA_DIR; в БД только пути и метаданные. is_real_work —
флаг реальной работы (НЕ для AI-визуализаций; последние всегда False).
expires_at — для временных файлов генерации (удаляются по retention).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class MediaFile(TimestampMixin, Base):
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stored_path: Mapped[str] = mapped_column(String(512), nullable=False)
    webp_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    jpg_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime: Mapped[str | None] = mapped_column(String(64), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    is_real_work: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    focus_x: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    focus_y: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
