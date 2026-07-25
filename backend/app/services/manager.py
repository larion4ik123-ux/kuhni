"""Resolve MAX recipients for new lead notifications."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Setting


async def manager_targets(db: AsyncSession, configured: list[int]) -> list[str | int]:
    """Combine environment recipients with a manager registered inside MAX."""
    targets: list[str | int] = list(configured)
    result = await db.execute(select(Setting).where(Setting.key == "max_manager_targets"))
    setting = result.scalar_one_or_none()
    if setting and setting.value:
        for raw in setting.value.split(","):
            value = raw.strip()
            if not value:
                continue
            target: str | int = int(value) if value.lstrip("-").isdigit() else value
            if target not in targets:
                targets.append(target)
    return targets


async def register_manager_target(db: AsyncSession, target: str | int) -> None:
    """Persist one verified MAX chat/user target without overwriting existing ones."""
    result = await db.execute(select(Setting).where(Setting.key == "max_manager_targets"))
    setting = result.scalar_one_or_none()
    values = (
        [item.strip() for item in (setting.value or "").split(",") if item.strip()]
        if setting
        else []
    )
    normalized = str(target)
    if normalized not in values:
        values.append(normalized)
    if setting is None:
        setting = Setting(key="max_manager_targets", category="messenger")
    setting.value = ",".join(values)
    db.add(setting)
