"""MAX Bot API adapter.

The adapter follows the public MAX Bot API: ``/messages`` for outgoing
messages, inline keyboards for choices, and ``request_contact`` for a verified
phone number. Incoming webhook updates are intentionally kept outside this
transport class so the funnel can remain messenger-neutral.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from .base import MessengerAdapter, MessengerButton, MessengerUserIdentity

if TYPE_CHECKING:
    from backend.app.core.settings import Settings


class MaxAdapter(MessengerAdapter):
    """HTTP transport for the official MAX Bot API."""

    messenger = "max"

    def __init__(self, settings: Settings) -> None:
        self._base_url = (settings.MAX_API_URL or "https://platform-api2.max.ru").rstrip("/")
        self._token = settings.MAX_BOT_TOKEN

    @property
    def _headers(self) -> dict[str, str]:
        if not self._token:
            raise RuntimeError("MAX_BOT_TOKEN is required to send MAX messages")
        return {"Authorization": self._token}

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30) as client:
            response = await client.request(method, path, headers=self._headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}

    @staticmethod
    def _keyboard(buttons: list[MessengerButton]) -> dict[str, Any]:
        return {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [[{"type": "callback", "text": button.text, "payload": button.payload}] for button in buttons]
            },
        }

    async def send_text(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        return await self._request("POST", "/messages", params={"chat_id": chat_id}, json={"text": text})

    async def send_image(
        self, chat_id: str | int, image_path: str, caption: str | None = None, **kwargs: Any
    ) -> Any:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(path)
        upload = await self._request("POST", "/uploads", params={"type": "image"})
        upload_url = upload["url"]
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(upload_url, files={"data": (path.name, path.read_bytes())})
            response.raise_for_status()
            uploaded = response.json() if response.content else {}
        token = uploaded.get("token") or upload.get("token")
        if not token:
            raise RuntimeError("MAX upload did not return an image token")
        return await self._request(
            "POST",
            "/messages",
            params={"chat_id": chat_id},
            json={"text": caption, "attachments": [{"type": "image", "payload": {"token": token}}]},
        )

    async def send_buttons(
        self, chat_id: str | int, text: str, buttons: list[MessengerButton], **kwargs: Any
    ) -> Any:
        return await self._request(
            "POST",
            "/messages",
            params={"chat_id": chat_id},
            json={"text": text, "attachments": [self._keyboard(buttons)]},
        )

    async def request_contact(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        attachment = {
            "type": "inline_keyboard",
            "payload": {"buttons": [[{"type": "request_contact", "text": "Отправить контакт"}]]},
        }
        return await self._request(
            "POST", "/messages", params={"chat_id": chat_id}, json={"text": text, "attachments": [attachment]}
        )

    async def edit_message(
        self,
        chat_id: str | int,
        message_id: str | int,
        text: str,
        buttons: list[MessengerButton] | None = None,
        **kwargs: Any,
    ) -> Any:
        body: dict[str, Any] = {"text": text}
        if buttons is not None:
            body["attachments"] = [self._keyboard(buttons)]
        return await self._request("PUT", "/messages", params={"message_id": message_id}, json=body)

    async def answer_callback(self, callback_id: str, text: str | None = None) -> None:
        body: dict[str, Any] = {}
        if text:
            body["notification"] = text
        await self._request("POST", "/answers", params={"callback_id": callback_id}, json=body)

    def get_user_identity(self, raw_update: Any) -> MessengerUserIdentity:
        user = raw_update.get("user", {}) if isinstance(raw_update, dict) else {}
        user_id = user.get("user_id") or user.get("id")
        if user_id is None:
            raise ValueError("MAX update has no user identifier")
        return MessengerUserIdentity(
            messenger=self.messenger,
            account_id=str(user_id),
            username=user.get("username"),
            first_name=user.get("first_name") or user.get("name"),
            last_name=user.get("last_name"),
        )
