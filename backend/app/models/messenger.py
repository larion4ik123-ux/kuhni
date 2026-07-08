"""Привязка пользователя к мессенджер-аккаунту.

UNIQUE(messenger, account_id) — один аккаунт в одном мессенджере = один user.
На этапе 2 добавится MAX; воронка и заявки работают по user_id и не меняются.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class MessengerAccount(TimestampMixin, Base):
    __tablename__ = "messenger_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    messenger: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="messenger_accounts")

    __table_args__ = (UniqueConstraint("messenger", "account_id", name="uq_messenger_account"),)
