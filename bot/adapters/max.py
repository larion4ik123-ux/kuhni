"""MAX messenger adapter placeholder.

The business services depend on MessengerAdapter, not Telegram-specific types.
This class marks the seam for stage 2: replacing these methods with real MAX
API calls should not change the funnel, lead or generation services.
"""

from __future__ import annotations

from typing import Any

from .base import MessengerAdapter, MessengerButton, MessengerUserIdentity


class MaxAdapter(MessengerAdapter):
    """Stage-2 MAX adapter stub."""

    messenger = "max"

    async def send_text(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        raise NotImplementedError("MAX adapter is not connected yet")

    async def send_image(
        self,
        chat_id: str | int,
        image_path: str,
        caption: str | None = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError("MAX adapter is not connected yet")

    async def send_buttons(
        self,
        chat_id: str | int,
        text: str,
        buttons: list[MessengerButton],
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError("MAX adapter is not connected yet")

    async def request_contact(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        raise NotImplementedError("MAX adapter is not connected yet")

    async def edit_message(
        self,
        chat_id: str | int,
        message_id: str | int,
        text: str,
        buttons: list[MessengerButton] | None = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError("MAX adapter is not connected yet")

    async def answer_callback(self, callback_id: str, text: str | None = None) -> None:
        raise NotImplementedError("MAX adapter is not connected yet")

    def get_user_identity(self, raw_update: Any) -> MessengerUserIdentity:
        raise NotImplementedError("MAX adapter is not connected yet")
