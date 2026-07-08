"""Lightweight placeholder for broadcast polling.

Broadcast delivery is intentionally separate from the FastAPI process. The
current implementation keeps the service boundary ready without sending any
messages until broadcast records and recipient selection are wired in admin.
"""

from __future__ import annotations

import asyncio
import logging

from backend.app.core.settings import get_settings
from shared.constants import WORKER_POLL_INTERVAL_SEC

logger = logging.getLogger(__name__)


async def run() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.LOG_LEVEL)
    logger.info("Broadcast worker started")
    while True:
        await asyncio.sleep(WORKER_POLL_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(run())
