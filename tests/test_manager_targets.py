from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.models import Base
from backend.app.services.manager import manager_targets, register_manager_target


def test_manager_target_can_be_registered_once() -> None:
    asyncio.run(_assert_manager_target_can_be_registered_once())


async def _assert_manager_target_can_be_registered_once() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as db:
        await register_manager_target(db, "user:42")
        await register_manager_target(db, "user:42")
        await db.commit()
        assert await manager_targets(db, [7]) == [7, "user:42"]
    await engine.dispose()
