"""ORM-модели SQLAlchemy 2. См. docs/DATABASE.md.

Изображения хранятся на диске (MEDIA_DIR); в БД — только пути и метаданные
(модель MediaFile). Пароли администраторов хешируются bcrypt (core.security).

Примечание: foreign-key ссылки на media_files внутри funnel/generation/etc.
оставлены как plain Integer (без ForeignKey-констрейнта), чтобы избежать
циклических зависимостей между моделями и сложных очередей создания таблиц;
целостность обеспечивается на уровне приложения.
"""

from __future__ import annotations

from .admin import Admin
from .audit_log import AuditLog
from .base import Base
from .broadcast import Broadcast, BroadcastRecipient
from .funnel import FunnelAnswer, FunnelOption, FunnelQuestion, FunnelSession
from .gallery import GalleryItem
from .generation import GeneratedImage, GenerationJob
from .job import Job
from .lead import Lead, LeadStatusHistory
from .media import MediaFile
from .messenger import MessengerAccount
from .review import Review
from .settings_model import Setting
from .site_block import FAQItem, ProcessStep, SiteBlock
from .user import User, UserContact

__all__ = [
    "Admin",
    "AuditLog",
    "Base",
    "Broadcast",
    "BroadcastRecipient",
    "FAQItem",
    "FunnelAnswer",
    "FunnelOption",
    "FunnelQuestion",
    "FunnelSession",
    "GalleryItem",
    "GeneratedImage",
    "GenerationJob",
    "Job",
    "Lead",
    "LeadStatusHistory",
    "MediaFile",
    "MessengerAccount",
    "ProcessStep",
    "Review",
    "Setting",
    "SiteBlock",
    "User",
    "UserContact",
]
