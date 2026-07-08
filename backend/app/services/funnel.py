"""Сервис воронки: навигация, условия, сохранение ответов."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import FunnelAnswer, FunnelQuestion, FunnelSession
from shared.schemas import AnswerPayload

if TYPE_CHECKING:
    from backend.app.repositories.repos import FunnelAnswerRepository, FunnelQuestionRepository


class FunnelService:
    """Бизнес-логика прохождения воронки. Мессенджер-независимая."""

    def __init__(
        self,
        db: AsyncSession,
        question_repo: "FunnelQuestionRepository",
        answer_repo: "FunnelAnswerRepository",
    ) -> None:
        self._db = db
        self._question_repo = question_repo
        self._answer_repo = answer_repo

    # ───────────────────────── Публичный API ─────────────────────────

    async def get_active_questions(self) -> list[FunnelQuestion]:
        """Все активные вопросы, отсортированные по order."""
        return await self._question_repo.get_active()

    async def get_next_question(
        self, session: FunnelSession, current: FunnelQuestion | None
    ) -> FunnelQuestion | None:
        """Возвращает следующий вопрос с учётом условий и правил навигации.

        Если current == None — возвращает первый активный.
        Если у current есть next_question_rule — переходим по нему.
        Иначе — следующий по order, для которого should_ask == True.
        """
        questions = await self.get_active_questions()
        if not questions:
            return None

        if current is None:
            return questions[0] if await self.should_ask(questions[0], session) else None

        # Проверяем правило навигации
        if current.next_question_rule:
            rule = current.next_question_rule
            next_key = rule.get("next_question_key")
            if next_key:
                for q in questions:
                    if q.key == next_key:
                        if await self.should_ask(q, session):
                            return q
                        break

        # Следующий по order
        found = False
        for q in questions:
            if found:
                if await self.should_ask(q, session):
                    return q
                continue
            if q.id == current.id:
                found = True

        return None

    async def should_ask(
        self, question: FunnelQuestion, session: FunnelSession
    ) -> bool:
        """Проверяет условие (condition) вопроса на основе уже данных ответов.

        Пустое condition → всегда показывать.
        Пример condition: {"question_key": "form", "option_code_in": ["corner", "u_shape"]}
        """
        if not question.condition:
            return True

        cond = question.condition
        question_key = cond.get("question_key")
        option_code_in = cond.get("option_code_in")
        option_code_not_in = cond.get("option_code_not_in")

        if not question_key:
            return True

        # Находим ответ на вопрос-условие
        answer = await self._get_answer_by_key(session.id, question_key)
        if answer is None:
            return False  # ещё не ответили — пока не показывать

        # Получаем выбранные option_ids и их internal_code
        selected_codes = await self._get_selected_codes(answer)

        if option_code_in is not None:
            return any(code in option_code_in for code in selected_codes)
        if option_code_not_in is not None:
            return not any(code in option_code_not_in for code in selected_codes)

        return True

    async def save_answer(
        self, session: FunnelSession, payload: AnswerPayload
    ) -> FunnelAnswer:
        """Сохраняет ответ пользователя."""
        answer = FunnelAnswer(
            session_id=session.id,
            question_id=payload.question_id,
            option_ids=payload.option_ids or None,
            value_text=payload.value_text,
            value_number=payload.value_number,
            media_file_id=payload.media_file_id,
        )
        self._db.add(answer)
        await self._db.flush()
        await self._db.refresh(answer)
        return answer

    async def get_session_summary(self, session: FunnelSession) -> dict:
        """Возвращает словарь с ответами сессии для отображения/промпта."""
        answers = await self._answer_repo.get_by_session(session.id)
        summary: dict = {}
        for a in answers:
            result = await self._db.execute(
                select(FunnelQuestion).where(FunnelQuestion.id == a.question_id)
            )
            question = result.scalar_one_or_none()
            if question is None:
                continue
            key = question.generation_key or question.key
            if a.option_ids:
                codes = await self._get_selected_codes(a)
                summary[key] = {
                    "question": question.title,
                    "codes": codes,
                }
            elif a.value_text:
                summary[key] = {"question": question.title, "text": a.value_text}
            elif a.value_number:
                summary[key] = {"question": question.title, "number": a.value_number}
        return summary

    # ───────────────────────── Внутренние ─────────────────────────

    async def _get_answer_by_key(self, session_id: int, question_key: str) -> FunnelAnswer | None:
        """Ответ сессии на вопрос с заданным key."""
        result = await self._db.execute(
            select(FunnelAnswer)
            .join(FunnelQuestion, FunnelAnswer.question_id == FunnelQuestion.id)
            .where(FunnelAnswer.session_id == session_id, FunnelQuestion.key == question_key)
        )
        return result.scalar_one_or_none()

    async def _get_selected_codes(self, answer: FunnelAnswer) -> list[str]:
        """Возвращает internal_code выбранных опций."""
        if not answer.option_ids:
            return []
        result = await self._db.execute(
            select(FunnelOption.internal_code)
            .where(FunnelOption.id.in_(answer.option_ids))
        )
        return [row[0] for row in result.all()]
