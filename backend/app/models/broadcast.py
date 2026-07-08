"""Рассылки и получатели.

Broadcast — рассылка с сегментом (all/with_contact/incomplete_funnel/got_result).
Статус: draft/scheduled/running/done/stopped/failed. BroadcastRecipient —
доставка одному пользователю (sent/failed/blocked). blocked — пользователь
заблокировал бота; исключается из будущих рассылок.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Broadcast(TimestampMixin, Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    media_file_id: Mapped[int | None] = mapped_column(nullable=True)
    buttons: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    segment: Mapped[str] = mapped_column(String(32), default="all", nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="draft")
    total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipients: Mapped[list["BroadcastRecipient"]] = relationship(
        back_populates="broadcast", cascade="all, delete-orphan"
    )


class BroadcastRecipient(TimestampMixin, Base):
    __tablename__ = "broadcast_recipients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    broadcast_id: Mapped[int] = mapped_column(
        ForeignKey("broadcasts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    messenger_account_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    broadcast: Mapped[Broadcast] = relationship(back_populates="recipients")
