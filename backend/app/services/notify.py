"""Сервис уведомлений: отправка менеджеру через мессенджер-адаптер.

Использует TYPE_CHECKING для MessengerAdapter, чтобы избежать циклической
зависимости. Адаптер MAX передаётся извне.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models import Lead

    # MessengerAdapter — адаптер конкретного мессенджера; передаётся извне
    class MessengerAdapter:
        async def send_text(self, chat_id: int, text: str) -> None: ...
        async def send_image(self, chat_id: int, image_path: str, caption: str) -> None: ...


class NotifyService:
    """Уведомления менеджеру о новых заявках и событиях."""

    def __init__(
        self,
        adapter: MessengerAdapter,
        manager_chat_ids: list[int],
    ) -> None:
        self._adapter = adapter
        self._manager_chat_ids = manager_chat_ids

    async def notify_new_lead(self, lead: Lead) -> None:
        """Отправляет карточку заявки менеджеру.

        Содержит: телефон, описание выбора, источник, ссылка на сессию.
        """
        text = self._build_lead_card(lead)
        for chat_id in self._manager_chat_ids:
            await self._adapter.send_text(chat_id, text)

    async def notify_generation_ready(self, lead: Lead, image_path: str | None) -> None:
        """Уведомляет менеджера, что генерация готова."""
        text = (
            f"Генерация готова для заявки #{lead.id}\n"
            f"Телефон: {lead.phone or 'не указан'}\n"
            f"Описание: {lead.selection_description or '—'}"
        )
        for chat_id in self._manager_chat_ids:
            if image_path:
                await self._adapter.send_image(chat_id, image_path, text)
            else:
                await self._adapter.send_text(chat_id, text)

    # ───────────────────────── Внутренние ─────────────────────────

    @staticmethod
    def _build_lead_card(lead: Lead) -> str:
        """Формирует текст карточки заявки для менеджера."""
        lines = [
            "Новая заявка",
            f"ID: #{lead.id}",
            f"Телефон: {lead.phone or 'не указан'}",
            f"Источник: {lead.source}",
            f"Статус: {lead.status}",
        ]
        if lead.selection_description:
            lines.append(f"Выбор: {lead.selection_description}")
        return "\n".join(lines)
