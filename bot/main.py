"""Telegram bot entrypoint."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from backend.app.core.settings import get_settings
from bot.handlers.funnel import router as funnel_router
from bot.middlewares.db import DbSessionMiddleware


async def main() -> None:
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to run the bot")

    logging.basicConfig(level=settings.LOG_LEVEL)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(DbSessionMiddleware())
    dispatcher.include_router(funnel_router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
