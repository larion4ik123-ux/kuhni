"""Пользователь (без аутентификации) и его контакты.

Идентификация — по мессенджер-аккаунту (MessengerAccount). Контакты (телефон)
передаются явно через request_contact в MAX; до этого генерация НЕ
запускается (инвариант GenerationService).
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    contacts: Mapped[list["UserContact"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    messenger_accounts: Mapped[list["MessengerAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserContact(TimestampMixin, Base):
    __tablename__ = "user_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped[User] = relationship(back_populates="contacts")

    __table_args__ = (Index("ix_user_contacts_user_created", "user_id", "created_at"),)
