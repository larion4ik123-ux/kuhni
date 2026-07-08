"""Keyboard helpers for funnel questions."""

from __future__ import annotations

from backend.app.models import FunnelOption
from bot.adapters import MessengerButton


def option_buttons(
    session_id: int,
    question_id: int,
    options: list[FunnelOption],
) -> list[MessengerButton]:
    """Build compact callback buttons for a single-choice question."""
    return [
        MessengerButton(
            text=option.title,
            payload=f"funnel:opt:{session_id}:{question_id}:{option.id}",
        )
        for option in options
        if option.active
    ]
