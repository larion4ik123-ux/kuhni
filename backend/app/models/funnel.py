"""Настраиваемая воронка: вопросы, варианты, сессии, ответы.

См. docs/FUNNEL.md. Вопросы и варианты редактируются в админпанели. condition
и next_question_rule — JSON (когда показывать / куда перейти). generation_hint
вариантов попадает в AI-промпт.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class FunnelQuestion(TimestampMixin, Base):
    __tablename__ = "funnel_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    media_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True
    )
    order: Mapped[int] = mapped_column(default=0, index=True, nullable=False)
    required: Mapped[bool] = mapped_column(default=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, index=True, nullable=False)
    allow_skip: Mapped[bool] = mapped_column(default=False, nullable=False)
    generation_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    condition: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    next_question_rule: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    options: Mapped[list["FunnelOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="FunnelOption.order"
    )


class FunnelOption(TimestampMixin, Base):
    __tablename__ = "funnel_options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("funnel_questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True
    )
    internal_code: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    generation_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    order: Mapped[int] = mapped_column(default=0, nullable=False)

    question: Mapped[FunnelQuestion] = relationship(back_populates="options")


class FunnelSession(TimestampMixin, Base):
    __tablename__ = "funnel_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    messenger_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("messenger_accounts.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="in_progress")
    source: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="unknown")
    current_question_id: Mapped[int | None] = mapped_column(
        ForeignKey("funnel_questions.id", ondelete="SET NULL"), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    answers: Mapped[list["FunnelAnswer"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class FunnelAnswer(TimestampMixin, Base):
    __tablename__ = "funnel_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("funnel_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("funnel_questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    option_ids: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_number: Mapped[float | None] = mapped_column(nullable=True)
    media_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True
    )

    session: Mapped[FunnelSession] = relationship(back_populates="answers")
