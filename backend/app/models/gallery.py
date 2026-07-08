"""Работы в галерее сайта.

layout (прямая/угловая/п-образная/остров), style (современный/неоклассика/
классика), primary_color — для фильтров галереи. is_real_work=True (работы
клиента); AI-визуализации в галерею не попадают.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class GalleryItem(TimestampMixin, Base):
    __tablename__ = "gallery_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    media_file_id: Mapped[int | None] = mapped_column(nullable=True)
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)
    layout: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    style: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    focus_x: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    focus_y: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_real_work: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
