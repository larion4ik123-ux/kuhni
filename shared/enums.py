"""Общие перечисления для платформы кухонь.

Все enum хранятся здесь, чтобы backend-сервисы, бот-адаптер и workers
использовали единые значения и не связывались с реализациями конкретных
мессенджеров или AI-провайдеров.
"""

from __future__ import annotations

from enum import StrEnum


# ───────────────────────── Мессенджеры ─────────────────────────


class Messenger(StrEnum):
    """Тип мессенджера. Этап 1 — telegram; этап 2 — max (без переписывания логики)."""

    TELEGRAM = "telegram"
    MAX = "max"


class FunnelSessionStatus(StrEnum):
    """Статус прохождения воронки."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class FunnelSource(StrEnum):
    """Источник захода в воронку (deep link / органика)."""

    WEBSITE_MAIN = "website_main"
    WEBSITE_GENERATOR = "website_generator"
    WEBSITE_GALLERY = "website_gallery"
    ORGANIC = "organic"
    UNKNOWN = "unknown"


# ───────────────────────── Типы вопросов воронки ─────────────────────────


class QuestionType(StrEnum):
    """Тип вопроса настраиваемой воронки. См. docs/FUNNEL.md."""

    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    NUMBER = "number"
    RANGE = "range"
    PHOTO = "photo"
    CONTACT = "contact"
    CONFIRMATION = "confirmation"


# ───────────────────────── Заявки ─────────────────────────


class LeadStatus(StrEnum):
    """Статус заявки. Редактируется менеджером / из админки."""

    NEW = "new"
    CONTACTED = "contacted"
    MEASUREMENT_SCHEDULED = "measurement_scheduled"
    QUOTE_SENT = "quote_sent"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


# ───────────────────────── Генерация / очередь ─────────────────────────


class JobType(StrEnum):
    """Тип фоновой задачи (таблица jobs, без Redis)."""

    GENERATION = "generation"
    BROADCAST = "broadcast"
    CLEANUP = "cleanup"
    BACKUP = "backup"


class JobStatus(StrEnum):
    """Статус фоновой задачи."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationProviderType(StrEnum):
    """Тип AI-провайдера генерации изображений. Меняется в настройках."""

    MOCK = "mock"
    OPENAI_COMPATIBLE = "openai_compatible"


# ───────────────────────── Медиа / категории ─────────────────────────


class MediaCategory(StrEnum):
    """Категория файла на диске. Соответствует папкам assets/raw."""

    OWNER = "owner"
    KITCHENS = "kitchens"
    LOGO = "logo"
    FACADES = "facades"
    COLORS = "colors"
    HANDLES = "handles"
    COUNTERTOPS = "countertops"
    REVIEWS = "reviews"
    GENERATED = "generated"
    UPLOAD = "upload"


# ───────────────────────── Рассылки ─────────────────────────


class BroadcastSegment(StrEnum):
    """Сегмент получателей рассылки."""

    ALL = "all"
    WITH_CONTACT = "with_contact"
    INCOMPLETE_FUNNEL = "incomplete_funnel"
    GOT_RESULT = "got_result"


class BroadcastStatus(StrEnum):
    """Статус рассылки."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    DONE = "done"
    STOPPED = "stopped"
    FAILED = "failed"


class BroadcastRecipientStatus(StrEnum):
    """Статус доставки одному получателю."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BLOCKED = "blocked"


# ───────────────────────── Отзывы ─────────────────────────


class ReviewSource(StrEnum):
    """Источник отзыва. Без выдуманных — только реальные."""

    YANDEX = "yandex"
    MANUAL = "manual"
    WIDGET = "widget"


# ───────────────────────── AI: параметры img2img ─────────────────────────


class AiQuality(StrEnum):
    """Качество генерации для polza.ai (Seedream)."""

    BASIC = "basic"  # 2K
    HIGH = "high"  # 4K


class AspectRatio(StrEnum):
    """Соотношение сторон генерации (polza.ai Seedream)."""

    R_1_1 = "1:1"
    R_4_3 = "4:3"
    R_3_4 = "3:4"
    R_3_2 = "3:2"
    R_2_3 = "2:3"
    R_16_9 = "16:9"
    R_9_16 = "9:16"
    R_21_9 = "21:9"
