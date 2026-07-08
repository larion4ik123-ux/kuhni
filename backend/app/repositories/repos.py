"""Репозитории для конкретных сущностей — тонкий слой CRUD."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import (
    Broadcast,
    BroadcastRecipient,
    FunnelAnswer,
    FunnelOption,
    FunnelQuestion,
    FunnelSession,
    GalleryItem,
    GenerationJob,
    Job,
    Lead,
    LeadStatusHistory,
    MediaFile,
    Review,
    SiteBlock,
    User,
    UserContact,
)

from .base import BaseRepository


# ───────────────────────── Воронка ─────────────────────────


class FunnelQuestionRepository:
    """CRUD вопросов воронки."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self) -> list[FunnelQuestion]:
        """Все активные вопросы, отсортированные по order."""
        result = await self._session.execute(
            select(FunnelQuestion)
            .where(FunnelQuestion.active == True)
            .order_by(FunnelQuestion.order)
        )
        return list(result.scalars().all())

    async def get_by_key(self, key: str) -> FunnelQuestion | None:
        """Вопрос по уникальному ключу."""
        result = await self._session.execute(
            select(FunnelQuestion).where(FunnelQuestion.key == key)
        )
        return result.scalar_one_or_none()


class FunnelSessionRepository(BaseRepository[FunnelSession]):
    """CRUD сессий воронки."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(FunnelSession, session)

    async def get_with_answers(self, session_id: int) -> FunnelSession | None:
        """Сессия с загруженными ответами (relationship)."""
        from sqlalchemy.orm import selectinload

        result = await self._session.execute(
            select(FunnelSession)
            .where(FunnelSession.id == session_id)
            .options(selectinload(FunnelSession.answers))
        )
        return result.scalar_one_or_none()


class FunnelAnswerRepository(BaseRepository[FunnelAnswer]):
    """CRUD ответов воронки."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(FunnelAnswer, session)

    async def get_by_session(self, session_id: int) -> list[FunnelAnswer]:
        """Все ответы сессии."""
        result = await self._session.execute(
            select(FunnelAnswer)
            .where(FunnelAnswer.session_id == session_id)
            .order_by(FunnelAnswer.created_at)
        )
        return list(result.scalars().all())


# ───────────────────────── Заявки ─────────────────────────


class LeadRepository(BaseRepository[Lead]):
    """CRUD заявок (leads)."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Lead, session)

    async def get_by_session(self, session_id: int) -> Lead | None:
        """Заявка по session_id (дедупликация)."""
        result = await self._session.execute(
            select(Lead).where(Lead.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_recent(
        self, user_id: int, hours: int = 24
    ) -> Lead | None:
        """Последняя заявка пользователя в окне дедупликации."""
        from datetime import datetime, timedelta, timezone

        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self._session.execute(
            select(Lead)
            .where(Lead.user_id == user_id, Lead.created_at >= since)
            .order_by(Lead.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        *,
        status: str | None = None,
        source: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """Список заявок с фильтрами."""
        stmt = select(Lead)
        if status:
            stmt = stmt.where(Lead.status == status)
        if source:
            stmt = stmt.where(Lead.source == source)
        stmt = stmt.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class LeadStatusHistoryRepository(BaseRepository[LeadStatusHistory]):
    """CRUD истории статусов заявки."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LeadStatusHistory, session)


# ───────────────────────── Рассылки ─────────────────────────


class BroadcastRepository(BaseRepository[Broadcast]):
    """CRUD рассылок."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Broadcast, session)


class BroadcastRecipientRepository(BaseRepository[BroadcastRecipient]):
    """CRUD получателей рассылки."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BroadcastRecipient, session)


# ───────────────────────── Галерея / Отзывы / Медиа ─────────────────────────


class GalleryRepository(BaseRepository[GalleryItem]):
    """CRUD элементов галереи."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(GalleryItem, session)


class ReviewRepository(BaseRepository[Review]):
    """CRUD отзывов."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Review, session)

    async def get_visible_with_source(self) -> list[Review]:
        """Видимые отзывы, у которых есть source_url."""
        result = await self._session.execute(
            select(Review)
            .where(Review.visible == True, Review.source_url.is_not(None))
            .order_by(Review.display_order)
        )
        return list(result.scalars().all())


class MediaRepository(BaseRepository[MediaFile]):
    """CRUD медиафайлов."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MediaFile, session)


# ───────────────────────── Очередь / Генерация ─────────────────────────


class JobRepository(BaseRepository[Job]):
    """CRUD фоновых задач (jobs)."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Job, session)


class GenerationJobRepository(BaseRepository[GenerationJob]):
    """CRUD задач генерации."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(GenerationJob, session)


# ───────────────────────── Пользователи / Контакты ─────────────────────────


class UserRepository(BaseRepository[User]):
    """CRUD пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)


class UserContactRepository(BaseRepository[UserContact]):
    """CRUD контактов пользователя."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserContact, session)

    async def get_by_user(self, user_id: int) -> list[UserContact]:
        """Все контакты пользователя."""
        result = await self._session.execute(
            select(UserContact)
            .where(UserContact.user_id == user_id)
            .order_by(UserContact.created_at.desc())
        )
        return list(result.scalars().all())
