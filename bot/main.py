"""MAX bot setup utility: validate token and register the production webhook."""

from __future__ import annotations

import argparse
import asyncio
import json

from backend.app.core.settings import get_settings
from bot.adapters.max import MaxAdapter


async def main(register: bool = False) -> None:
    settings = get_settings()
    if not settings.MAX_BOT_TOKEN:
        raise RuntimeError("MAX_BOT_TOKEN is required")
    adapter = MaxAdapter(settings)
    print(json.dumps(await adapter.get_me(), ensure_ascii=False, indent=2))
    if register:
        if not settings.MAX_WEBHOOK_URL or not settings.MAX_WEBHOOK_SECRET:
            raise RuntimeError("MAX_WEBHOOK_URL and MAX_WEBHOOK_SECRET are required")
        result = await adapter.register_webhook(
            settings.MAX_WEBHOOK_URL, settings.MAX_WEBHOOK_SECRET
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--register-webhook", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(register=args.register_webhook))
