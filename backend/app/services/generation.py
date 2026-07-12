"""Сервис генерации: создание job, формирование промпта, постановка в очередь.

Критический инвариант: без контакта пользователя генерация НЕ запускается.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import (
    FunnelAnswer,
    FunnelOption,
    FunnelQuestion,
    GenerationJob,
    Job,
    MediaFile,
    UserContact,
)
from shared.constants import AI_DEFAULT_MASTER_PROMPT, AI_KITCHEN_REFERENCE_EXAMPLES
from shared.schemas import SelectionSummary

if TYPE_CHECKING:
    from backend.app.core.settings import Settings
    from backend.app.repositories.repos import GenerationJobRepository, JobRepository


class GenerationService:
    """Бизнес-логика генерации изображений."""

    def __init__(
        self,
        db: AsyncSession,
        gen_repo: GenerationJobRepository,
        job_repo: JobRepository,
        settings: Settings,
    ) -> None:
        self._db = db
        self._gen_repo = gen_repo
        self._job_repo = job_repo
        self._settings = settings

    async def create_job(
        self,
        lead_id: int | None,
        session_id: int | None,
        user_id: int,
    ) -> GenerationJob | None:
        """Создаёт задачу генерации. БЕЗ контакта — возвращает None, НЕ ставит в очередь.

        Это критический инвариант: проверяем наличие user_contacts.
        """
        # Проверка контакта
        has_contact = await self._has_contact(user_id)
        if not has_contact:
            return None

        # Формируем описание и промпт из ответов сессии
        answers = await self._get_session_answers(session_id)
        summary = self.build_selection_summary(answers)
        prompt = self.build_prompt(answers, self._settings.AI_MASTER_PROMPT)
        reference_image_path = self._extract_reference_image_path(answers)
        params = {
            "aspect_ratio": self._extract_aspect_ratio(answers),
            "quality": self._settings.AI_QUALITY,
            "selection_summary": summary.text,
        }
        if reference_image_path:
            params["reference_image_path"] = reference_image_path

        # Создаём generation job
        gen_job = await self._gen_repo.create(
            lead_id=lead_id,
            user_id=user_id,
            session_id=session_id,
            status="pending",
            provider=self._settings.AI_PROVIDER,
            model=self._settings.AI_MODEL,
            prompt=prompt,
            params=params,
        )

        # Ставим в очередь фоновых задач
        await self.enqueue_job(gen_job.id)
        return gen_job

    def build_selection_summary(self, answers: list[dict]) -> SelectionSummary:
        """Формирует человекочитаемое описание выбора клиента.

        Пример: «Угловая кухня в современном стиле, серые фасады AGT,
        чёрные квадратные ручки, светлая столешница, фурнитура Blum.»
        """
        parts: dict[str, str] = {}
        for ans in answers:
            key = ans.get("key", "")
            if not key:
                continue
            title = ans.get("question_title", "")
            codes = ans.get("option_codes", [])
            text = ans.get("value_text", "")
            if codes:
                parts[key] = f"{title}: {', '.join(codes)}"
            elif text:
                parts[key] = f"{title}: {text}"

        # Собираем в естественный порядок
        order = [
            "width",
            "height",
            "area",
            "form",
            "style",
            "color",
            "facade",
            "handle",
            "countertop",
            "hardware",
            "budget",
        ]
        ordered_parts = []
        for key in order:
            if key in parts:
                ordered_parts.append(parts[key])
        # Дополнительные пожелания
        if "wishes" in parts:
            ordered_parts.append(parts["wishes"])

        text = "; ".join(ordered_parts) if ordered_parts else "Выбор не указан"
        return SelectionSummary(text=text, parts=parts)

    def build_prompt(self, answers: list[dict], master_prompt: str | None = None) -> str:
        """Формирует итоговый промпт для AI из ответов + мастер-промпта.

        Добавляет generation_hint каждого выбранного варианта + параметры.
        """
        master = master_prompt or AI_DEFAULT_MASTER_PROMPT
        hints: list[str] = []
        for ans in answers:
            hint = ans.get("generation_hint", "")
            if hint:
                hints.append(hint)
        extra = "\n".join(f"- {hint}" for hint in hints) if hints else "- Без дополнительных подсказок"
        summary = self.build_selection_summary(answers)
        examples = "\n".join(f"- {example}" for example in AI_KITCHEN_REFERENCE_EXAMPLES)

        # Параметры из ответов
        params: list[str] = []
        for ans in answers:
            if ans.get("key") in {"size", "width", "height", "area"} and ans.get("value_text"):
                params.append(f"{ans['question_title']}: {ans['value_text']}")
            if ans.get("key") == "room_type" and ans.get("option_codes"):
                params.append(f"Тип помещения: {', '.join(ans['option_codes'])}")
            if ans.get("key") == "wishes" and ans.get("value_text"):
                params.append(f"Дополнительные пожелания: {ans['value_text']}")
        params_text = "\n".join(f"- {item}" for item in params) if params else "- Не указаны"

        return f"""
{master}

Заявка клиента:
{summary.text}

Выбранные визуальные подсказки:
{extra}

Дополнительные параметры:
{params_text}

Примеры реальных кухонь клиента по качеству и стилю:
{examples}

Сделай один коммерчески сильный вариант: кухня должна выглядеть изготовленной на заказ, аккуратной, пригодной для расчёта и демонстрации клиенту. Не подписывай изображение текстом.
""".strip()

    async def enqueue_job(self, job_id: int) -> Job:
        """Записывает задачу в таблицу jobs (фоновая очередь)."""
        return await self._job_repo.create(
            type="generation",
            payload={"generation_job_id": job_id},
            status="pending",
            max_attempts=self._settings.AI_RETRY_COUNT + 1,
        )

    # ───────────────────────── Внутренние ─────────────────────────

    async def _has_contact(self, user_id: int) -> bool:
        """Проверяет, есть ли у пользователя хотя бы один контакт."""
        result = await self._db.execute(
            select(UserContact).where(UserContact.user_id == user_id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _get_session_answers(self, session_id: int | None) -> list[dict]:
        """Возвращает ответы сессии с enriched данными (question, options)."""
        if session_id is None:
            return []
        result = await self._db.execute(
            select(FunnelAnswer)
            .where(FunnelAnswer.session_id == session_id)
            .order_by(FunnelAnswer.created_at)
        )
        answers = result.scalars().all()
        enriched: list[dict] = []
        for a in answers:
            q_result = await self._db.execute(
                select(FunnelQuestion).where(FunnelQuestion.id == a.question_id)
            )
            question = q_result.scalar_one_or_none()
            if question is None:
                continue

            item: dict = {
                "key": question.generation_key or question.key,
                "question_title": question.title,
                "question_type": question.type,
            }
            if a.option_ids:
                o_result = await self._db.execute(
                    select(FunnelOption).where(FunnelOption.id.in_(a.option_ids))
                )
                options = o_result.scalars().all()
                item["option_codes"] = [o.internal_code for o in options]
                item["generation_hint"] = "\n".join(
                    [o.generation_hint for o in options if o.generation_hint]
                )
            if a.value_text:
                item["value_text"] = a.value_text
            if a.value_number:
                item["value_number"] = a.value_number
            if a.media_file_id:
                media = await self._db.get(MediaFile, a.media_file_id)
                if media is not None:
                    item["media_file_id"] = media.id
                    item["media_stored_path"] = media.stored_path
                    item["media_category"] = media.category
            enriched.append(item)
        return enriched

    def _extract_reference_image_path(self, answers: list[dict]) -> str | None:
        """Возвращает локальный путь к фото помещения, если оно скачано с мессенджера."""
        for ans in answers:
            stored_path = ans.get("media_stored_path")
            if not stored_path or str(stored_path).startswith("telegram:"):
                continue
            path = Path(stored_path)
            if path.exists():
                return str(path)
        return None

    def _extract_aspect_ratio(self, answers: list[dict]) -> str:
        """Пытается определить aspect_ratio из ответов (по умолчанию 4:3)."""
        for ans in answers:
            if ans.get("key") == "form":
                codes = ans.get("option_codes", [])
                if "island" in codes or "u_shape" in codes:
                    return "16:9"
                if "corner" in codes:
                    return "4:3"
        return "4:3"
