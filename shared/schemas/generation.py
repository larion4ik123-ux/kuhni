"""Схемы генерации изображений.

SelectionSummary — человекочитаемое описание выбора (для менеджера и заявки).
GenerationRequest — вход для провайдера (промпт + референсное фото + параметры).
GenerationResultOut — результат (пути к файлам + стоимость + статус).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from shared.enums import AspectRatio, JobStatus


class SelectionSummary(BaseModel):
    """Человекочитаемое описание выбора клиента.

    Пример: «Угловая кухня в современном стиле, серые фасады AGT, чёрные
    квадратные ручки, светлая столешница, фурнитура Blum.»
    """

    text: str
    parts: dict[str, str] = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """Вход для ImageGenerationProvider.

    prompt — итоговый промпт (мастер + generation_hint + параметры + инструкция
    сохранить помещение). reference_image_path — путь к фото помещения на диске.
    """

    prompt: str
    reference_image_path: str | None = None
    aspect_ratio: AspectRatio = AspectRatio.R_4_3
    quality: str = "basic"
    n: int = 1


class GenerationResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    status: JobStatus
    image_urls: list[str] = Field(default_factory=list)
    cost: float | None = None
    error: str | None = None
    prompt: str | None = None
    created_at: datetime | None = None
    finished_at: datetime | None = None
