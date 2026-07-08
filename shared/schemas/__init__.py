"""Общие Pydantic-схемы (DTO) для всего монорепозитория.

Эти схемы — контракт между слоями: сервисы возвращают/принимают их,
API и бот-адаптер сериализуют в свой формат. Схемы НЕ зависят от ORM-моделей
и мессенджера — разделяют ответственность.
"""

from __future__ import annotations

from .funnel import (
    AnswerPayload,
    FunnelAnswerOut,
    FunnelOptionOut,
    FunnelQuestionOut,
    FunnelSessionOut,
    NextQuestionRule,
    QuestionCondition,
)
from .generation import GenerationRequest, GenerationResultOut, SelectionSummary
from .lead import LeadOut, LeadStatusUpdate
from .media import MediaFileOut
from .site import (
    ContactsOut,
    FAQItemOut,
    GalleryItemOut,
    MaterialOptionOut,
    ProcessStepOut,
    ReviewOut,
    SiteBlockOut,
    SiteContentOut,
)

__all__ = [
    "AnswerPayload",
    "ContactsOut",
    "FAQItemOut",
    "FunnelAnswerOut",
    "FunnelOptionOut",
    "FunnelQuestionOut",
    "FunnelSessionOut",
    "GalleryItemOut",
    "GenerationRequest",
    "GenerationResultOut",
    "LeadOut",
    "LeadStatusUpdate",
    "MaterialOptionOut",
    "MediaFileOut",
    "NextQuestionRule",
    "ProcessStepOut",
    "QuestionCondition",
    "ReviewOut",
    "SelectionSummary",
    "SiteBlockOut",
    "SiteContentOut",
]
