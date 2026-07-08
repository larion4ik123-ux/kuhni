"""Схемы воронки подбора кухни.

FunnelQuestionOut / FunnelOptionOut — то, что мессенджер-адаптер рендерит
в кнопки/сообщения, а API отдаёт в админку. Условия и правила навигации —
JSON-объекты (см. docs/FUNNEL.md).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from shared.enums import FunnelSessionStatus, FunnelSource, QuestionType


class QuestionCondition(BaseModel):
    """Когда показывать вопрос. Пустое → всегда.

    Пример: question_key="form", option_code_in=["corner","u_shape"].
    """

    question_key: str | None = None
    option_code_in: list[str] | None = None
    option_code_not_in: list[str] | None = None


class NextQuestionRule(BaseModel):
    """Куда перейти после вопроса. По умолчанию — следующий по order.

    Пример: on_option="classic", next_question_key="facade_classic".
    """

    on_option: str | None = None
    next_question_key: str | None = None


class FunnelOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    internal_code: str
    generation_hint: str | None = None
    active: bool = True
    order: int = 0


class FunnelQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    title: str
    description: str | None = None
    type: QuestionType
    image_url: str | None = None
    order: int
    required: bool = True
    active: bool = True
    allow_skip: bool = False
    generation_key: str | None = None
    condition: QuestionCondition | None = None
    next_question_rule: NextQuestionRule | None = None
    options: list[FunnelOptionOut] = Field(default_factory=list)


class AnswerPayload(BaseModel):
    """Ответ пользователя на один вопрос.

    Для single_choice — option_ids=[id]; multiple_choice — несколько;
    text/number/range — value; photo — media_file_id; contact — phone.
    """

    question_id: int
    option_ids: list[int] = Field(default_factory=list)
    value_text: str | None = None
    value_number: float | None = None
    media_file_id: int | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class FunnelAnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question_id: int
    question_key: str | None = None
    question_title: str | None = None
    option_ids: list[int] = Field(default_factory=list)
    option_titles: list[str] = Field(default_factory=list)
    option_codes: list[str] = Field(default_factory=list)
    generation_hints: list[str] = Field(default_factory=list)
    value_text: str | None = None
    value_number: float | None = None
    media_file_id: int | None = None
    media_url: str | None = None


class FunnelSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    messenger: str
    status: FunnelSessionStatus
    source: FunnelSource
    current_question_id: int | None = None
    answers: list[FunnelAnswerOut] = Field(default_factory=list)
    has_contact: bool = False
    has_photo: bool = False

    # сырые данные условий (для отладки/админки)
    raw: dict[str, Any] | None = None
