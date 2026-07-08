"""Схемы заявок (leads)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared.enums import LeadStatus


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    session_id: int | None = None
    phone: str | None = None
    status: LeadStatus
    source: str
    selection_description: str | None = None
    generation_job_id: int | None = None
    manager_comment: str | None = None
    created_at: datetime
    updated_at: datetime

    # удобные поля для отображения менеджеру
    user_display_name: str | None = None
    username: str | None = None
    messenger: str | None = None
    photo_url: str | None = None
    result_url: str | None = None


class LeadStatusUpdate(BaseModel):
    """Смена статуса заявки (из админки / менеджером)."""

    status: LeadStatus
    comment: str | None = None
