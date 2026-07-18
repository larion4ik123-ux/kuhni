"""Провайдер для polza.ai (OpenAI-compatible API).

Поддерживает text-to-image (sync + polling) и img2img (async + polling).
Сохраняет результат в MEDIA_DIR/generated/<job_id>/.
"""

from __future__ import annotations

import asyncio
import base64
import pathlib
import uuid
from typing import TYPE_CHECKING

import httpx

from shared.schemas import GenerationRequest

from .base import GenerationResult, ImageGenerationProvider

if TYPE_CHECKING:
    from backend.app.core.settings import Settings


class OpenAICompatibleGenerationProvider(ImageGenerationProvider):
    """Провайдер для polza.ai / Seedream.

    - text-to-image: POST /v2/images/generations (sync 120с), затем polling GET /v1/media/{id}
    - img2img: POST /v1/media (async), затем polling GET /v1/media/{id}
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.AI_TIMEOUT),
            headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
        )
        self._poll_interval = 4.0
        self._max_poll = 600.0

    def validate_config(self) -> bool:
        """Проверяет наличие base_url и api_key."""
        return bool(self._settings.AI_API_BASE_URL and self._settings.AI_API_KEY)

    def estimate_cost(self, request: GenerationRequest) -> float | None:
        """Пока не реализовано — возвращаем None."""
        return None

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Отправляет запрос и ждёт результат (polling)."""
        base = self._settings.AI_API_BASE_URL.rstrip("/")

        if request.reference_image_path:
            result = await self._img2img(base, request)
        else:
            result = await self._text2img(base, request)

        return result

    async def _text2img(self, base: str, request: GenerationRequest) -> GenerationResult:
        """Text-to-image через /v2/images/generations."""
        url = self._images_url(base)
        payload = {
            "model": self._settings.AI_MODEL,
            "prompt": request.prompt,
            "n": request.n,
            "size": self._aspect_to_size(request.aspect_ratio),
            "quality": request.quality or self._settings.AI_QUALITY,
        }

        for attempt in range(self._settings.AI_RETRY_COUNT + 1):
            try:
                resp = await self._client.post(url, json=payload, timeout=120.0)
            except httpx.TimeoutException:
                if attempt == self._settings.AI_RETRY_COUNT:
                    return self._error("Таймаут text-to-image после всех попыток")
                await asyncio.sleep(2 ** attempt)
                continue

            status_code = resp.status_code
            if status_code == 402:
                return self._error("Недостаточно средств на счету (402)")
            if status_code == 429:
                return self._error("Превышен лимит запросов (429)")
            if status_code in (502, 503):
                if attempt == self._settings.AI_RETRY_COUNT:
                    return self._error(f"Провайдер недоступен ({status_code})")
                await asyncio.sleep(2 ** attempt)
                continue

            resp.raise_for_status()
            data = resp.json()

            # Если сразу готов — возвращаем
            if data.get("data") and isinstance(data["data"], list):
                paths = await self._save_images(data["data"], request)
                return GenerationResult(
                    image_paths=paths,
                    remote_ids=[],
                    cost=None,
                    status="done",
                    error=None,
                )

            # Иначе polling по id
            remote_id = data.get("id")
            if not remote_id:
                return self._error("Нет id в ответе провайдера")
            return await self._poll_media(base, remote_id, request)

        return self._error("Не удалось выполнить text-to-image")

    async def _img2img(self, base: str, request: GenerationRequest) -> GenerationResult:
        """Img2img через /v1/media (async)."""
        ref_path = pathlib.Path(request.reference_image_path)
        if not ref_path.exists():
            return self._error(f"Референсное фото не найдено: {ref_path}")

        b64 = base64.b64encode(ref_path.read_bytes()).decode()
        url = self._media_url(base)
        payload = {
            "model": self._settings.AI_MODEL or "bytedance/seedream-4.5",
            "input": {
                "prompt": request.prompt[:3000],
                "aspect_ratio": str(request.aspect_ratio),
                "quality": request.quality or self._settings.AI_QUALITY,
                "images": [{"type": "base64", "data": b64}],
            },
            "async": True,
        }

        for attempt in range(self._settings.AI_RETRY_COUNT + 1):
            try:
                resp = await self._client.post(url, json=payload)
            except httpx.TimeoutException:
                if attempt == self._settings.AI_RETRY_COUNT:
                    return self._error("Таймаут img2img после всех попыток")
                await asyncio.sleep(2 ** attempt)
                continue

            status_code = resp.status_code
            if status_code == 402:
                return self._error("Недостаточно средств (402)")
            if status_code == 429:
                return self._error("Превышен лимит (429)")
            if status_code in (502, 503):
                if attempt == self._settings.AI_RETRY_COUNT:
                    return self._error(f"Провайдер недоступен ({status_code})")
                await asyncio.sleep(2 ** attempt)
                continue

            resp.raise_for_status()
            data = resp.json()
            remote_id = data.get("id")
            if not remote_id:
                return self._error("Нет id в ответе провайдера")
            return await self._poll_media(base, remote_id, request)

        return self._error("Не удалось выполнить img2img")

    async def _poll_media(self, base: str, remote_id: str, request: GenerationRequest) -> GenerationResult:
        """Polling GET /v1/media/{id} каждые 4 секунд до 600 секунд."""
        url = f"{self._media_url(base)}/{remote_id}"
        elapsed = 0.0
        while elapsed < self._max_poll:
            await asyncio.sleep(self._poll_interval)
            elapsed += self._poll_interval

            try:
                resp = await self._client.get(url)
            except httpx.TimeoutException:
                continue

            if resp.status_code in (502, 503):
                continue

            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "unknown")

            if status in {"done", "completed"}:
                images = (
                    data.get("output", {}).get("images", [])
                    or data.get("data", [])
                    or data.get("result", {}).get("images", [])
                )
                if images:
                    paths = await self._save_images(images, request)
                    return GenerationResult(
                        image_paths=paths,
                        remote_ids=[remote_id],
                        cost=None,
                        status="done",
                        error=None,
                    )
                return self._error("Генерация завершена, но провайдер не вернул изображение")

            if status in ("failed", "error", "cancelled"):
                return self._error(data.get("error", "Ошибка генерации"))

        return self._error("Таймаут polling (600с)")

    async def _save_images(self, images: list, request: GenerationRequest) -> list[str]:
        """Скачивает и сохраняет изображения в MEDIA_DIR/generated/<job_id>/."""
        media_dir = pathlib.Path(self._settings.MEDIA_DIR) / "generated" / uuid.uuid4().hex
        media_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        for idx, img in enumerate(images):
            if isinstance(img, dict):
                img_url = img.get("url") or img.get("uri")
                b64_data = img.get("b64_json")
            else:
                img_url = str(img)
                b64_data = None

            out_path = media_dir / f"result_{idx}.jpg"

            if b64_data:
                out_path.write_bytes(base64.b64decode(b64_data))
                paths.append(str(out_path))
            elif img_url:
                if img_url.startswith("http"):
                    img_resp = await self._client.get(img_url)
                    img_resp.raise_for_status()
                    out_path.write_bytes(img_resp.content)
                else:
                    out_path.write_bytes(base64.b64decode(img_url))
                paths.append(str(out_path))

        return paths

    @staticmethod
    def _aspect_to_size(aspect_ratio) -> str:
        """Преобразует AspectRatio в строку размера для API."""
        mapping = {
            "1:1": "1024x1024",
            "4:3": "1024x768",
            "3:4": "768x1024",
            "3:2": "1152x768",
            "2:3": "768x1152",
            "16:9": "1280x720",
            "9:16": "720x1280",
            "21:9": "1792x768",
        }
        return mapping.get(str(aspect_ratio), "1024x768")

    @staticmethod
    def _media_url(base: str) -> str:
        normalized = base.rstrip("/")
        if normalized.endswith("/api/v1"):
            return f"{normalized}/media"
        if normalized.endswith("/api"):
            return f"{normalized}/v1/media"
        return f"{normalized}/api/v1/media"

    @staticmethod
    def _images_url(base: str) -> str:
        normalized = base.rstrip("/")
        if normalized.endswith("/api/v1"):
            normalized = normalized.removesuffix("/v1")
        elif not normalized.endswith("/api"):
            normalized = f"{normalized}/api"
        return f"{normalized}/v2/images/generations"

    def _error(self, message: str) -> GenerationResult:
        """Вспомогательный конструктор ошибки."""
        return GenerationResult(
            image_paths=[],
            remote_ids=[],
            cost=None,
            status="failed",
            error=message,
        )

    async def get_status(self, job_remote_id: str) -> str:
        """Возвращает статус удалённой задачи."""
        base = self._settings.AI_API_BASE_URL.rstrip("/")
        url = f"{self._media_url(base)}/{job_remote_id}"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            return resp.json().get("status", "unknown")
        except httpx.HTTPError:
            return "unknown"

    async def cancel(self, job_remote_id: str) -> bool:
        """Пытается отменить задачу."""
        base = self._settings.AI_API_BASE_URL.rstrip("/")
        url = f"{self._media_url(base)}/{job_remote_id}/cancel"
        try:
            resp = await self._client.post(url)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        """Закрывает httpx-клиент."""
        await self._client.aclose()
