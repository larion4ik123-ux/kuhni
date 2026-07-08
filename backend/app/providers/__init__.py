"""Провайдеры генерации изображений."""

from __future__ import annotations

from .base import GenerationResult, ImageGenerationProvider
from .factory import get_provider
from .mock import MockGenerationProvider
from .openai_compatible import OpenAICompatibleGenerationProvider

__all__ = [
    "GenerationResult",
    "ImageGenerationProvider",
    "MockGenerationProvider",
    "OpenAICompatibleGenerationProvider",
    "get_provider",
]
