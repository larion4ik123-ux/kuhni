"""Фабрика провайдеров генерации изображений."""

from __future__ import annotations

from backend.app.core.settings import Settings

from .base import ImageGenerationProvider
from .mock import MockGenerationProvider
from .openai_compatible import OpenAICompatibleGenerationProvider


def get_provider(settings: Settings) -> ImageGenerationProvider:
    """Возвращает провайдер в зависимости от AI_PROVIDER в настройках."""
    if settings.AI_PROVIDER == "openai_compatible":
        return OpenAICompatibleGenerationProvider(settings)
    return MockGenerationProvider(settings.MEDIA_DIR)
