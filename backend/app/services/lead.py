"""Сервис заявок (leads): создание, дедупликация, экспорт."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Lead, LeadStatusHistory, UserContact
from shared.schemas import LeadOut

if TYPE_CHECKING:
    from backend.app.repositories.repos import LeadRepository, LeadStatusHistoryRepository


class LeadService:
    """Бизнес-логика заявок. Идемпотентность: проверка по session_id и окну дедупликации."""

    def __init__(
        self,
        db: AsyncSession,
        lead_repo: "LeadRepository",
        history_repo: "LeadStatusHistoryRepository",
    ) -> None:
        self._db = db
        self._lead_repo = lead_repo
        self._history_repo = history_repo

    async def create_lead_from_session(
        self,
        session_id: int,
        user_id: int,
        source: str,
        selection_description: str | None = None,
    ) -> Lead | None:
        """Создаёт заявку из сессии. Идемпотентная: не создаёт дубли.

        Проверка:
        1. По session_id (если уже есть — вернуть существующую).
        2. По user_id + окно дедупликации (24ч).
        """
        # Проверка по session_id
        existing = await self._lead_repo.get_by_session(session_id)
        if existing is not None:
            return existing

        # Проверка по user_id + окно
        from shared.constants import LEAD_DEDUP_WINDOW_HOURS

        recent = await self._lead_repo.get_by_user_recent(user_id, hours=LEAD_DEDUP_WINDOW_HOURS)
        if recent is not None:
            return recent

        # Получаем телефон пользователя (последний контакт)
        phone = await self._get_user_phone(user_id)

        lead = await self._lead_repo.create(
            user_id=user_id,
            session_id=session_id,
            phone=phone,
            status="new",
            source=source,
            selection_description=selection_description,
        )

        # История статусов
        await self._history_repo.create(
            lead_id=lead.id,
            old_status=None,
            new_status="new",
            changed_by=None,
            comment="Создано автоматически из воронки",
        )

        return lead

    async def update_status(
        self,
        lead_id: int,
        new_status: str,
        changed_by: int | None = None,
        comment: str | None = None,
    ) -> Lead | None:
        """Обновляет статус заявки и пишет в историю."""
        lead = await self._lead_repo.get(lead_id)
        if lead is None:
            return None

        old_status = lead.status
        lead = await self._lead_repo.update(lead, status=new_status)

        await self._history_repo.create(
            lead_id=lead.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            comment=comment,
        )
        return lead

    async def get_leads(
        self,
        *,
        status: str | None = None,
        source: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """Список заявок с фильтрами."""
        return await self._lead_repo.get_filtered(
            status=status, source=source, limit=limit, offset=offset
        )

    async def export_csv(self, leads: list[Lead] | None = None) -> str:
        """Экспортирует заявки в CSV (строка)."""
        if leads is None:
            leads = await self._lead_repo.get_filtered(limit=10000)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["id", "user_id", "session_id", "phone", "status", "source", "selection", "created_at"]
        )
        for lead in leads:
            writer.writerow(
                [
                    lead.id,
                    lead.user_id,
                    lead.session_id,
                    lead.phone or "",
                    lead.status,
                    lead.source,
                    lead.selection_description or "",
                    lead.created_at.isoformat() if lead.created_at else "",
                ]
            )
        return output.getvalue()

    # ───────────────────────── Внутренние ─────────────────────────

    async def _get_user_phone(self, user_id: int) -> str | None:
        """Последний телефон пользователя."""
        result = await self._db.execute(
            select(UserContact)
            .where(UserContact.user_id == user_id)
            .order_by(UserContact.created_at.desc())
            .limit(1)
        )
        contact = result.scalar_one_or_none()
        return contact.phone if contact else None
