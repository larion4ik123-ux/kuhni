"""Messenger-neutral adapter contract.

The funnel, lead creation and generation services must not know whether the
user talks through Telegram, MAX or another messenger. Adapters translate
service-level messages into platform-specific calls.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MessengerButton:
    """A button rendered by a messenger adapter."""

    text: str
    payload: str


@dataclass(frozen=True)
class MessengerUserIdentity:
    """Stable identity extracted from a messenger update."""

    messenger: str
    account_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class MessengerAdapter(ABC):
    """Messenger-independent output interface."""

    messenger: str

    @abstractmethod
    async def send_text(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        """Send a plain text message."""

    @abstractmethod
    async def send_image(
        self,
        chat_id: str | int,
        image_path: str,
        caption: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send an image from local path or platform-supported file id."""

    @abstractmethod
    async def send_buttons(
        self,
        chat_id: str | int,
        text: str,
        buttons: list[MessengerButton],
        **kwargs: Any,
    ) -> Any:
        """Send text with callback buttons."""

    @abstractmethod
    async def request_contact(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        """Ask the user to share a verified messenger contact."""

    @abstractmethod
    async def edit_message(
        self,
        chat_id: str | int,
        message_id: str | int,
        text: str,
        buttons: list[MessengerButton] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Edit an existing message when supported."""

    @abstractmethod
    async def answer_callback(self, callback_id: str, text: str | None = None) -> None:
        """Acknowledge a callback/button press."""

    @abstractmethod
    def get_user_identity(self, raw_update: Any) -> MessengerUserIdentity:
        """Extract a stable account identity from a platform update."""
