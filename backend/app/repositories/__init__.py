"""Репозитории платформы."""

from __future__ import annotations

from .base import BaseRepository
from .repos import (
    BroadcastRecipientRepository,
    BroadcastRepository,
    FunnelAnswerRepository,
    FunnelQuestionRepository,
    FunnelSessionRepository,
    GalleryRepository,
    GenerationJobRepository,
    JobRepository,
    LeadRepository,
    LeadStatusHistoryRepository,
    MediaRepository,
    ReviewRepository,
    UserContactRepository,
    UserRepository,
)

__all__ = [
    "BaseRepository",
    "BroadcastRecipientRepository",
    "BroadcastRepository",
    "FunnelAnswerRepository",
    "FunnelQuestionRepository",
    "FunnelSessionRepository",
    "GalleryRepository",
    "GenerationJobRepository",
    "JobRepository",
    "LeadRepository",
    "LeadStatusHistoryRepository",
    "MediaRepository",
    "ReviewRepository",
    "UserContactRepository",
    "UserRepository",
]
