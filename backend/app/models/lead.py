"""Заявка (lead) и история смены статусов.

Lead создаётся ПОСЛЕ получения контакта. generation_job_id — одна заявка →
одна генерация (другой вариант = новый lead/job). Идемпотентность: проверка
по (session_id) / окну дедупликации — защита от повторных Telegram updates.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="new")
    source: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="unknown")
    selection_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_job_id: Mapped[int | None] = mapped_column(nullable=True)
    manager_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status_history: Mapped[list["LeadStatusHistory"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    old_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    changed_by: Mapped[int | None] = mapped_column(nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    lead: Mapped[Lead] = relationship(back_populates="status_history")
