"""FSM states for the Telegram funnel adapter."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class FunnelStates(StatesGroup):
    waiting_text = State()
    waiting_photo = State()
    waiting_contact = State()
