"""aiogram middleware that injects an AsyncSession into handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from backend.app.core.database import async_session_factory


class DbSessionMiddleware(BaseMiddleware):
    """Open one database session per Telegram update."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            data["db"] = session
            result = await handler(event, data)
            await session.commit()
            return result
