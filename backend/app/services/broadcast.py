"""Сервис рассылок: сегментация, создание, статистика."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Broadcast, BroadcastRecipient, FunnelSession, Lead, User, UserContact
from shared.enums import BroadcastSegment, BroadcastStatus

if TYPE_CHECKING:
    from backend.app.repositories.repos import BroadcastRepository, BroadcastRecipientRepository


class BroadcastService:
    """Бизнес-логика рассылок."""

    def __init__(
        self,
        db: AsyncSession,
        broadcast_repo: "BroadcastRepository",
        recipient_repo: "BroadcastRecipientRepository",
    ) -> None:
        self._db = db
        self._broadcast_repo = broadcast_repo
        self._recipient_repo = recipient_repo

    async def build_recipients(self, segment: str) -> list[int]:
        """Возвращает список user_id для сегмента.

        Сегменты:
        - all: все пользователи
        - with_contact: у кого есть телефон
        - incomplete_funnel: начали воронку, но не завершили
        - got_result: есть lead со статусом != new
        """
        if segment == BroadcastSegment.ALL:
            result = await self._db.execute(select(User.id))
            return [row[0] for row in result.all()]

        if segment == BroadcastSegment.WITH_CONTACT:
            result = await self._db.execute(
                select(UserContact.user_id).distinct()
            )
            return [row[0] for row in result.all()]

        if segment == BroadcastSegment.INCOMPLETE_FUNNEL:
            result = await self._db.execute(
                select(FunnelSession.user_id)
                .where(FunnelSession.status != "completed")
                .distinct()
            )
            return [row[0] for row in result.all()]

        if segment == BroadcastSegment.GOT_RESULT:
            result = await self._db.execute(
                select(Lead.user_id)
                .where(Lead.status != "new")
                .distinct()
            )
            return [row[0] for row in result.all()]

        return []

    async def create_broadcast(
        self,
        title: str,
        text: str,
        segment: str,
        media_file_id: int | None = None,
        buttons: list[dict] | None = None,
    ) -> Broadcast:
        """Создаёт рассылку и записывает получателей."""
        user_ids = await self.build_recipients(segment)

        broadcast = await self._broadcast_repo.create(
            title=title,
            text=text,
            media_file_id=media_file_id,
            buttons=buttons,
            segment=segment,
            status=BroadcastStatus.DRAFT,
            total=len(user_ids),
            sent=0,
            failed=0,
        )

        for user_id in user_ids:
            await self._recipient_repo.create(
                broadcast_id=broadcast.id,
                user_id=user_id,
                status="pending",
            )

        return broadcast

    async def get_stats(self, broadcast_id: int) -> dict:
        """Возвращает статистику рассылки."""
        broadcast = await self._broadcast_repo.get(broadcast_id)
        if broadcast is None:
            return {}

        result = await self._db.execute(
            select(BroadcastRecipient)
            .where(BroadcastRecipient.broadcast_id == broadcast_id)
        )
        recipients = result.scalars().all()

        sent = sum(1 for r in recipients if r.status == "sent")
        failed = sum(1 for r in recipients if r.status == "failed")
        blocked = sum(1 for r in recipients if r.status == "blocked")
        pending = sum(1 for r in recipients if r.status == "pending")

        return {
            "broadcast_id": broadcast.id,
            "title": broadcast.title,
            "segment": broadcast.segment,
            "status": broadcast.status,
            "total": broadcast.total,
            "sent": sent,
            "failed": failed,
            "blocked": blocked,
            "pending": pending,
            "started_at": broadcast.started_at,
            "finished_at": broadcast.finished_at,
        }
