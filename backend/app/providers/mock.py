"""Mock-провайдер: возвращает ссылку на существующее изображение.

Используется для разработки и тестов. Не требует API-ключа.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from shared.schemas import GenerationRequest

from .base import GenerationResult, ImageGenerationProvider


class MockGenerationProvider(ImageGenerationProvider):
    """Всегда валиден. Копирует референсное изображение в MEDIA_DIR/generated."""

    def __init__(self, media_dir: str = "./media") -> None:
        self._media_dir = Path(media_dir)
        self._ref = Path("assets/processed/kitchens/kitchen_01_fullscreen.jpg")

    def validate_config(self) -> bool:
        """Mock всегда валиден."""
        return True

    def estimate_cost(self, request: GenerationRequest) -> float | None:
        """Mock бесплатен."""
        return 0.0

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Копирует референсное изображение в папку generated/<job_id>."""
        out_dir = self._media_dir / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / "mock_result.jpg"
        if self._ref.exists():
            shutil.copy2(self._ref, dst)
        return GenerationResult(
            image_paths=[str(dst)],
            remote_ids=["mock"],
            cost=0.0,
            status="done",
            error=None,
        )

    async def get_status(self, job_remote_id: str) -> str:
        """Mock всегда готов."""
        return "done"

    async def cancel(self, job_remote_id: str) -> bool:
        """Mock нечего отменять."""
        return True
