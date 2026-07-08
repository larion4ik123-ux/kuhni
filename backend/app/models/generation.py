"""Задачи генерации (очередь) и результаты.

generation_jobs — очередь (status: pending/running/done/failed/cancelled).
prompt — итоговый промпт (мастер + generation_hint + параметры). params — JSON
с референсным фото, аспектом и т.д. generated_images хранит N вариантов.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class GenerationJob(TimestampMixin, Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="pending")
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="mock")
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    params: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_media_file_id: Mapped[int | None] = mapped_column(nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    images: Mapped[list["GeneratedImage"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class GeneratedImage(TimestampMixin, Base):
    __tablename__ = "generated_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("generation_jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    media_file_id: Mapped[int | None] = mapped_column(nullable=True)
    variant_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    job: Mapped[GenerationJob] = relationship(back_populates="images")
