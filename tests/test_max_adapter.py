from __future__ import annotations

import asyncio
import json

import httpx

from backend.app.core.settings import Settings
from bot.adapters.base import MessengerButton
from bot.adapters.max import MaxAdapter


def test_max_adapter_uses_official_auth_and_user_target() -> None:
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": {"body": {"mid": "1"}}})

    adapter = MaxAdapter(
        Settings(MAX_BOT_TOKEN="secret"),
        transport=httpx.MockTransport(handler),
    )
    asyncio.run(
        adapter.send_buttons(
            "user:42", "Выберите", [MessengerButton("Угловая", "kitchen:option:1:2")]
        )
    )

    assert captured["authorization"] == "secret"
    assert "user_id=42" in captured["url"]
    assert captured["body"]["attachments"][0]["type"] == "inline_keyboard"


def test_webhook_registration_has_required_update_types() -> None:
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"success": True})

    adapter = MaxAdapter(
        Settings(MAX_BOT_TOKEN="secret"),
        transport=httpx.MockTransport(handler),
    )
    asyncio.run(adapter.register_webhook("https://example.ru/api/max/webhook", "shared"))

    assert captured["secret"] == "shared"
    assert set(captured["update_types"]) == {
        "bot_started",
        "message_created",
        "message_callback",
    }
