"""Базовый репозиторий с generic CRUD."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD для любой ORM-модели."""

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get(self, pk: int) -> ModelT | None:
        """Получить запись по первичному ключу."""
        return await self._session.get(self._model, pk)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Получить список с пагинацией."""
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelT:
        """Создать запись и вернуть объект."""
        obj = self._model(**kwargs)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, obj: ModelT, **kwargs) -> ModelT:
        """Обновить поля объекта и вернуть его."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        """Удалить объект."""
        await self._session.delete(obj)
        await self._session.flush()
