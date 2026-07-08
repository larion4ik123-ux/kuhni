"""Редактируемые блоки сайта + FAQ + этапы работы.

SiteBlock — key/value контент (hero_title, about_text, ...). FAQItem и
ProcessStep — отдельные сущности со своим порядком.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class SiteBlock(TimestampMixin, Base):
    __tablename__ = "site_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_file_id: Mapped[int | None] = mapped_column(nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class FAQItem(TimestampMixin, Base):
    __tablename__ = "faq_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ProcessStep(TimestampMixin, Base):
    __tablename__ = "process_steps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
