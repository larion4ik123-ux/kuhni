"""Схемы медиафайлов.

В БД хранятся только пути и метаданные; сами файлы — на диске (MEDIA_DIR).
media_url строится как MEDIA_BASE_URL + stored_path.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from shared.enums import MediaCategory


class MediaFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: MediaCategory
    original_filename: str | None = None
    url: str | None = None
    webp_url: str | None = None
    jpg_url: str | None = None
    mime: str | None = None
    width: int | None = None
    height: int | None = None
    size_bytes: int | None = None
    is_real_work: bool = False
    focus_x: float = 0.5
    focus_y: float = 0.5
