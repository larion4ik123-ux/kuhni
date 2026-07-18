"""Схемы контента сайта.

SiteContentOut — агрегированный публичный контент (отдаётся frontend через API).
Все ключи редактируются в админпанели (таблица site_blocks).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SiteBlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    title: str | None = None
    content: str | None = None
    image_url: str | None = None
    webp_url: str | None = None
    order: int = 0
    visible: bool = True


class GalleryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str | None = None
    webp_url: str | None = None
    caption: str | None = None
    layout: str | None = None
    style: str | None = None
    primary_color: str | None = None
    alt_text: str | None = None
    display_order: int = 0
    is_real_work: bool = True
    visible: bool = True
    focus_x: float = 0.5
    focus_y: float = 0.5


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    text: str
    rating: int
    review_date: str | None = None
    source: str
    source_url: str | None = None
    display_order: int = 0


class FAQItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    display_order: int = 0


class ProcessStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    step_number: int
    icon: str | None = None


class MaterialOptionOut(BaseModel):
    """Вариант выбора материала/фурнитуры (для блока материалов сайта и воронки)."""

    id: int
    group: str  # facade / handle / countertop / hardware / color / layout / style
    title: str
    description: str | None = None
    image_url: str | None = None
    internal_code: str | None = None
    generation_hint: str | None = None
    active: bool = True
    display_order: int = 0


class ContactsOut(BaseModel):
    phone: str | None = None
    max_url: str | None = None
    address: str | None = None
    region: str | None = None
    hours: str | None = None
    yandex_maps_url: str | None = None
    yandex_widget_html: str | None = None


class SiteContentOut(BaseModel):
    """Агрегированный публичный контент — отдаётся frontend через /api/site."""

    blocks: dict[str, SiteBlockOut] = Field(default_factory=dict)
    advantages: list[SiteBlockOut] = Field(default_factory=list)
    gallery: list[GalleryItemOut] = Field(default_factory=list)
    reviews: list[ReviewOut] = Field(default_factory=list)
    faq: list[FAQItemOut] = Field(default_factory=list)
    process_steps: list[ProcessStepOut] = Field(default_factory=list)
    materials: list[MaterialOptionOut] = Field(default_factory=list)
    contacts: ContactsOut = Field(default_factory=ContactsOut)
    max_bot_url: str | None = None
    # флаг: показывать ли блок отзывов (только если есть реальные со ссылкой)
    show_reviews: bool = False
    show_yandex_button: bool = False
