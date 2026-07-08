"""Сервис контента сайта: блоки, галерея, отзывы, FAQ, материалы, контакты."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import FAQItem, GalleryItem, ProcessStep, Review, SiteBlock, UserContact
from shared.schemas import ContactsOut, FAQItemOut, GalleryItemOut, MaterialOptionOut, ProcessStepOut, ReviewOut, SiteBlockOut, SiteContentOut

if TYPE_CHECKING:
    from backend.app.core.settings import Settings


class ContentService:
    """Агрегирует публичный контент сайта."""

    def __init__(self, db: AsyncSession, settings: "Settings") -> None:
        self._db = db
        self._settings = settings

    async def get_site_content(self) -> SiteContentOut:
        """Возвращает агрегированный контент для frontend.

        - blocks: site_blocks по ключу
        - gallery: видимые работы
        - reviews: только со source_url (иначе show_reviews=False)
        - faq: видимые вопросы
        - process_steps: этапы работы
        - materials: опции материалов (из funnel_options с generation_key)
        - contacts: телефон, Telegram/MAX, адрес
        - telegram_bot_url/max_bot_url: из настроек
        - show_reviews: есть ли отзывы со ссылкой
        - show_yandex_button: есть ли yandex_maps_url
        """
        # Блоки сайта
        blocks_result = await self._db.execute(
            select(SiteBlock).where(SiteBlock.visible == True).order_by(SiteBlock.order)
        )
        blocks = {b.key: self._to_block_out(b) for b in blocks_result.scalars().all()}

        # Галерея (только реальные работы)
        gallery_result = await self._db.execute(
            select(GalleryItem)
            .where(GalleryItem.visible == True, GalleryItem.is_real_work == True)
            .order_by(GalleryItem.display_order)
        )
        gallery = [self._to_gallery_out(g) for g in gallery_result.scalars().all()]

        # Отзывы (только со ссылкой)
        reviews_result = await self._db.execute(
            select(Review)
            .where(Review.visible == True, Review.source_url.is_not(None))
            .order_by(Review.display_order)
        )
        reviews_raw = reviews_result.scalars().all()
        reviews = [self._to_review_out(r) for r in reviews_raw]
        show_reviews = len(reviews) > 0

        # FAQ
        faq_result = await self._db.execute(
            select(FAQItem).where(FAQItem.visible == True).order_by(FAQItem.display_order)
        )
        faq = [self._to_faq_out(f) for f in faq_result.scalars().all()]

        # Этапы работы
        steps_result = await self._db.execute(
            select(ProcessStep).order_by(ProcessStep.display_order)
        )
        steps = [self._to_step_out(s) for s in steps_result.scalars().all()]

        # Материалы (заглушка — из funnel_options или отдельной таблицы)
        materials: list[MaterialOptionOut] = []

        # Контакты
        contacts = ContactsOut(
            phone=blocks.get("contacts_phone", SiteBlockOut(key="contacts_phone")).content,
            telegram_url=blocks.get("contacts_telegram", SiteBlockOut(key="contacts_telegram")).content,
            max_url=blocks.get("contacts_max", SiteBlockOut(key="contacts_max")).content,
            address=blocks.get("contacts_address", SiteBlockOut(key="contacts_address")).content,
            region=blocks.get("contacts_region", SiteBlockOut(key="contacts_region")).content,
            hours=blocks.get("contacts_hours", SiteBlockOut(key="contacts_hours")).content,
            yandex_maps_url=blocks.get("yandex_maps_url", SiteBlockOut(key="yandex_maps_url")).content,
            yandex_widget_html=blocks.get("yandex_widget_html", SiteBlockOut(key="yandex_widget_html")).content,
        )
        show_yandex_button = bool(contacts.yandex_maps_url)

        return SiteContentOut(
            blocks=blocks,
            advantages=[],  # заполняется из blocks с префиксом advantage_
            gallery=gallery,
            reviews=reviews,
            faq=faq,
            process_steps=steps,
            materials=materials,
            contacts=contacts,
            telegram_bot_url=self._settings.TELEGRAM_BOT_URL or None,
            max_bot_url=self._settings.MAX_BOT_URL or None,
            show_reviews=show_reviews,
            show_yandex_button=show_yandex_button,
        )

    async def update_block(self, key: str, content: str | None) -> SiteBlock | None:
        """Обновляет содержимое блока сайта."""
        result = await self._db.execute(
            select(SiteBlock).where(SiteBlock.key == key)
        )
        block = result.scalar_one_or_none()
        if block is None:
            return None
        block.content = content
        self._db.add(block)
        await self._db.flush()
        await self._db.refresh(block)
        return block

    async def add_review(
        self,
        author_name: str,
        text: str,
        rating: int,
        source: str = "manual",
        source_url: str | None = None,
    ) -> Review:
        """Добавляет отзыв (без фейковых данных)."""
        review = Review(
            author_name=author_name,
            text=text,
            rating=rating,
            source=source,
            source_url=source_url,
        )
        self._db.add(review)
        await self._db.flush()
        await self._db.refresh(review)
        return review

    async def upload_image(self, file_path: str, category: str) -> None:
        """Заглушка для загрузки изображения (создаёт MediaFile)."""
        from backend.app.models import MediaFile

        media = MediaFile(
            category=category,
            stored_path=file_path,
        )
        self._db.add(media)
        await self._db.flush()

    # ───────────────────────── Внутренние конвертеры ─────────────────────────

    @staticmethod
    def _to_block_out(block: SiteBlock) -> SiteBlockOut:
        return SiteBlockOut(
            key=block.key,
            title=block.title,
            content=block.content,
            image_url=None,  # media_file_id не используется в блоках
            order=block.order,
            visible=block.visible,
        )

    @staticmethod
    def _to_gallery_out(item: GalleryItem) -> GalleryItemOut:
        return GalleryItemOut(
            id=item.id,
            image_url=None,  # media_file_id
            webp_url=None,
            caption=item.caption,
            layout=item.layout,
            style=item.style,
            primary_color=item.primary_color,
            alt_text=item.alt_text,
            display_order=item.display_order,
            is_real_work=item.is_real_work,
            focus_x=0.5,
            focus_y=0.5,
        )

    @staticmethod
    def _to_review_out(review: Review) -> ReviewOut:
        return ReviewOut(
            id=review.id,
            author_name=review.author_name,
            text=review.text,
            rating=review.rating,
            review_date=review.review_date,
            source=review.source,
            source_url=review.source_url,
            display_order=review.display_order,
        )

    @staticmethod
    def _to_faq_out(item: FAQItem) -> FAQItemOut:
        return FAQItemOut(
            id=item.id,
            question=item.question,
            answer=item.answer,
            display_order=item.display_order,
        )

    @staticmethod
    def _to_step_out(step: ProcessStep) -> ProcessStepOut:
        return ProcessStepOut(
            id=step.id,
            title=step.title,
            description=step.description,
            step_number=step.step_number,
            icon=step.icon,
        )
