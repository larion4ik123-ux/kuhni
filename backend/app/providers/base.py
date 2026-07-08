"""Абстрактный провайдер генерации изображений."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.schemas import GenerationRequest


@dataclass
class GenerationResult:
    """Результат генерации одного или нескольких изображений."""

    image_paths: list[str]
    """Пути к сохранённым файлам на диске."""
    remote_ids: list[str]
    """Идентификаторы задач на стороне провайдера."""
    cost: float | None
    """Стоимость в условных единицах (или None)."""
    status: str
    """Статус: done / pending / failed / cancelled."""
    error: str | None
    """Описание ошибки (если status == failed)."""


class ImageGenerationProvider(ABC):
    """Интерфейс провайдера генерации изображений."""

    @abstractmethod
    async def generate(self, request: "GenerationRequest") -> GenerationResult:
        """Запускает генерацию и возвращает результат (или polling-заглушку)."""
        ...

    @abstractmethod
    async def get_status(self, job_remote_id: str) -> str:
        """Возвращает статус удалённой задачи (pending / running / done / failed)."""
        ...

    @abstractmethod
    def validate_config(self) -> bool:
        """Проверяет, что провайдер сконфигурирован корректно."""
        ...

    @abstractmethod
    def estimate_cost(self, request: "GenerationRequest") -> float | None:
        """Оценивает стоимость запроса (или None, если не поддерживается)."""
        ...

    @abstractmethod
    async def cancel(self, job_remote_id: str) -> bool:
        """Отменяет удалённую задачу. Возвращает True при успехе."""
        ...
