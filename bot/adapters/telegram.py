"""Telegram implementation of MessengerAdapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .base import MessengerAdapter, MessengerButton, MessengerUserIdentity


class TelegramAdapter(MessengerAdapter):
    """Telegram adapter backed by aiogram 3.x."""

    messenger = "telegram"

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send_text(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        return await self._bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def send_image(
        self,
        chat_id: str | int,
        image_path: str,
        caption: str | None = None,
        **kwargs: Any,
    ) -> Any:
        photo = FSInputFile(image_path) if Path(image_path).exists() else image_path
        return await self._bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, **kwargs)

    async def send_buttons(
        self,
        chat_id: str | int,
        text: str,
        buttons: list[MessengerButton],
        **kwargs: Any,
    ) -> Any:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=button.text, callback_data=button.payload)]
                for button in buttons
            ]
        )
        return await self._bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, **kwargs)

    async def request_contact(self, chat_id: str | int, text: str, **kwargs: Any) -> Any:
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отправить телефон", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        return await self._bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, **kwargs)

    async def edit_message(
        self,
        chat_id: str | int,
        message_id: str | int,
        text: str,
        buttons: list[MessengerButton] | None = None,
        **kwargs: Any,
    ) -> Any:
        reply_markup = None
        if buttons:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=button.text, callback_data=button.payload)]
                    for button in buttons
                ]
            )
        return await self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=int(message_id),
            text=text,
            reply_markup=reply_markup,
            **kwargs,
        )

    async def answer_callback(self, callback_id: str, text: str | None = None) -> None:
        await self._bot.answer_callback_query(callback_query_id=callback_id, text=text)

    def get_user_identity(self, raw_update: Any) -> MessengerUserIdentity:
        user = raw_update.from_user
        return MessengerUserIdentity(
            messenger=self.messenger,
            account_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
