"""MAX webhook funnel: one calm question at a time, then lead + visualization."""

from __future__ import annotations

import hashlib
import logging
import mimetypes
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.core.settings import Settings
from backend.app.models import (
    FunnelAnswer,
    FunnelOption,
    FunnelQuestion,
    FunnelSession,
    MediaFile,
    MessengerAccount,
    User,
    UserContact,
)
from backend.app.repositories.repos import (
    GenerationJobRepository,
    JobRepository,
    LeadRepository,
    LeadStatusHistoryRepository,
)
from backend.app.services.generation import GenerationService
from backend.app.services.lead import LeadService
from backend.app.services.notify import NotifyService
from bot.adapters.base import MessengerButton
from bot.adapters.max import MaxAdapter

PHONE_RE = re.compile(r"\+?[\d\s()\-]{10,22}")
logger = logging.getLogger(__name__)


class MaxFunnelHandler:
    """Persisted MAX flow with no price calculation and no message deletion."""

    def __init__(self, db: AsyncSession, adapter: MaxAdapter, settings: Settings) -> None:
        self.db = db
        self.adapter = adapter
        self.settings = settings

    async def handle_update(self, update: dict[str, Any]) -> None:
        update_type = update.get("update_type")
        identity = self.adapter.get_user_identity(update)
        account = await self._account(identity)
        chat_id = self._chat_id(update, identity.account_id)

        if update_type == "bot_started":
            source = self._start_payload(update)
            session = await self._new_or_active_session(account, source)
            await self.adapter.send_text(
                chat_id,
                "Здравствуйте! Я Артём Ермаков. Помогу собрать идею кухни под ваше помещение. "
                "Это займёт несколько минут: без калькулятора и случайной цены.",
            )
            await self._show_current_or_first(chat_id, session)
            return

        session = await self._new_or_active_session(account, "max")
        if update_type == "message_callback":
            await self._handle_callback(update, chat_id, session)
        elif update_type == "message_created":
            await self._handle_message(update, chat_id, session, account)

    async def _handle_callback(
        self, update: dict[str, Any], chat_id: str | int, session: FunnelSession
    ) -> None:
        callback = update.get("callback") or {}
        callback_id = str(callback.get("callback_id") or "")
        payload = str(callback.get("payload") or "")
        parts = payload.split(":")
        if callback_id:
            await self.adapter.answer_callback(callback_id)

        if payload == "kitchen:restart":
            await self.db.execute(delete(FunnelAnswer).where(FunnelAnswer.session_id == session.id))
            session.status = "in_progress"
            session.completed_at = None
            session.current_question_id = None
            await self.db.flush()
            await self._show_current_or_first(chat_id, session)
            return

        if payload == "kitchen:confirm":
            await self._finish(chat_id, session)
            return

        if len(parts) != 4 or parts[:2] != ["kitchen", "option"]:
            await self.adapter.send_text(chat_id, "Кнопка устарела. Продолжим с текущего шага.")
            await self._show_current_or_first(chat_id, session)
            return

        question_id, option_id = int(parts[2]), int(parts[3])
        question = await self._question(question_id)
        current = await self._current_question(session)
        option = await self.db.get(FunnelOption, option_id)
        if (
            question is None
            or current is None
            or current.id != question.id
            or option is None
            or option.question_id != question.id
        ):
            await self.adapter.send_text(chat_id, "Не удалось прочитать выбор. Нажмите вариант ещё раз.")
            await self._show_current_or_first(chat_id, session)
            return
        await self._save_answer(session, question, option_ids=[option.id])
        await self._advance(chat_id, session, question)

    async def _handle_message(
        self,
        update: dict[str, Any],
        chat_id: str | int,
        session: FunnelSession,
        account: MessengerAccount,
    ) -> None:
        question = await self._current_question(session)
        if question is None:
            await self._show_current_or_first(chat_id, session)
            return
        message = update.get("message") or {}
        body = message.get("body") or {}
        text = str(body.get("text") or "").strip()
        attachments = body.get("attachments") or message.get("attachments") or []

        if question.type == "contact":
            phone = self._extract_phone(text, attachments)
            if not phone:
                await self.adapter.request_contact(
                    chat_id, "Нажмите «Отправить контакт», чтобы Артём мог связаться по вашему проекту."
                )
                return
            await self._save_contact(account.user_id, phone, account)
            await self._save_answer(session, question, value_text=phone)
            await self._advance(chat_id, session, question)
            return

        if question.type == "photo":
            image_url = self._extract_image_url(attachments)
            if not image_url:
                await self.adapter.send_text(
                    chat_id,
                    "Пришлите одну фотографию помещения обычным изображением. Лучше снять стену целиком, "
                    "чтобы были видны пол, потолок, окно и двери.",
                )
                return
            media = await self._download_image(image_url, session.id)
            await self._save_answer(session, question, media_file_id=media.id)
            await self._advance(chat_id, session, question)
            return

        if question.type in {"text", "number"}:
            if not text:
                await self.adapter.send_text(chat_id, "Напишите ответ одним сообщением.")
                return
            if question.key in {"width", "height", "area"} and not re.search(r"\d", text):
                await self.adapter.send_text(chat_id, "Нужна примерная цифра. Например: 320 см или 12 м².")
                return
            await self._save_answer(session, question, value_text=text[:1000])
            await self._advance(chat_id, session, question)
            return

        await self._show_question(chat_id, session, question)

    async def _show_current_or_first(self, chat_id: str | int, session: FunnelSession) -> None:
        question = await self._current_question(session)
        if question is None:
            question = await self._first_question()
            if question is None:
                await self.adapter.send_text(chat_id, "Анкета временно недоступна. Артём уже получил обращение.")
                return
            session.current_question_id = question.id
            await self.db.flush()
        await self._show_question(chat_id, session, question)

    async def _show_question(
        self, chat_id: str | int, session: FunnelSession, question: FunnelQuestion
    ) -> None:
        if question.type == "single_choice":
            buttons = [
                MessengerButton(option.title, f"kitchen:option:{question.id}:{option.id}")
                for option in question.options
                if option.active
            ]
            await self.adapter.send_buttons(chat_id, question.title, buttons)
        elif question.type == "contact":
            await self.adapter.request_contact(chat_id, question.title)
        elif question.type == "confirmation":
            await self.adapter.send_buttons(
                chat_id,
                f"{question.title}\n\n{await self._summary(session)}",
                [
                    MessengerButton("Всё верно", "kitchen:confirm"),
                    MessengerButton("Начать заново", "kitchen:restart"),
                ],
            )
        else:
            description = f"\n{question.description}" if question.description else ""
            await self.adapter.send_text(chat_id, f"{question.title}{description}")

    async def _advance(
        self, chat_id: str | int, session: FunnelSession, current: FunnelQuestion
    ) -> None:
        result = await self.db.execute(
            select(FunnelQuestion)
            .where(FunnelQuestion.active.is_(True), FunnelQuestion.order > current.order)
            .options(selectinload(FunnelQuestion.options))
            .order_by(FunnelQuestion.order)
            .limit(1)
        )
        next_question = result.scalar_one_or_none()
        session.current_question_id = next_question.id if next_question else None
        await self.db.flush()
        if next_question:
            await self._show_question(chat_id, session, next_question)
        else:
            await self._finish(chat_id, session)

    async def _finish(self, chat_id: str | int, session: FunnelSession) -> None:
        if session.status == "completed":
            await self.adapter.send_text(chat_id, "Заявка уже сохранена. Артём увидит её в MAX.")
            return
        summary = await self._summary(session)
        lead_service = LeadService(
            self.db, LeadRepository(self.db), LeadStatusHistoryRepository(self.db)
        )
        lead = await lead_service.create_lead_from_session(
            session.id, session.user_id, session.source, summary
        )
        if lead is None:
            raise RuntimeError("Lead creation failed")
        session.status = "completed"
        session.completed_at = datetime.now(UTC)
        session.current_question_id = None

        generation = GenerationService(
            self.db,
            GenerationJobRepository(self.db),
            JobRepository(self.db),
            self.settings,
        )
        generation_job = await generation.create_job(lead.id, session.id, session.user_id)
        if generation_job:
            lead.generation_job_id = generation_job.id
        try:
            await NotifyService(
                self.adapter, self.settings.MAX_MANAGER_CHAT_IDS
            ).notify_new_lead(lead)
        except httpx.HTTPError:
            logger.exception("MAX manager notification failed; lead remains persisted")
        await self.db.flush()
        await self.adapter.send_text(
            chat_id,
            "Готово. Я сохранил параметры и фото помещения. Визуальный вариант будет подготовлен "
            "по вашему запросу, а Артём увидит заявку и свяжется с вами, чтобы уточнить детали.",
        )

    async def _account(self, identity) -> MessengerAccount:
        result = await self.db.execute(
            select(MessengerAccount).where(
                MessengerAccount.messenger == "max",
                MessengerAccount.account_id == identity.account_id,
            )
        )
        account = result.scalar_one_or_none()
        if account is None:
            user = User()
            self.db.add(user)
            await self.db.flush()
            account = MessengerAccount(
                user_id=user.id,
                messenger="max",
                account_id=identity.account_id,
                username=identity.username,
                first_name=identity.first_name,
                last_name=identity.last_name,
            )
            self.db.add(account)
            await self.db.flush()
        return account

    async def _new_or_active_session(
        self, account: MessengerAccount, source: str
    ) -> FunnelSession:
        result = await self.db.execute(
            select(FunnelSession)
            .where(
                FunnelSession.messenger_account_id == account.id,
                FunnelSession.status == "in_progress",
            )
            .order_by(FunnelSession.created_at.desc())
            .limit(1)
        )
        session = result.scalar_one_or_none()
        if session is None:
            session = FunnelSession(
                user_id=account.user_id,
                messenger_account_id=account.id,
                source=source[:64] or "max",
            )
            self.db.add(session)
            await self.db.flush()
        return session

    async def _first_question(self) -> FunnelQuestion | None:
        result = await self.db.execute(
            select(FunnelQuestion)
            .where(FunnelQuestion.active.is_(True))
            .options(selectinload(FunnelQuestion.options))
            .order_by(FunnelQuestion.order)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _current_question(self, session: FunnelSession) -> FunnelQuestion | None:
        return await self._question(session.current_question_id) if session.current_question_id else None

    async def _question(self, question_id: int | None) -> FunnelQuestion | None:
        if question_id is None:
            return None
        result = await self.db.execute(
            select(FunnelQuestion)
            .where(FunnelQuestion.id == question_id)
            .options(selectinload(FunnelQuestion.options))
        )
        return result.scalar_one_or_none()

    async def _save_answer(
        self,
        session: FunnelSession,
        question: FunnelQuestion,
        *,
        option_ids: list[int] | None = None,
        value_text: str | None = None,
        media_file_id: int | None = None,
    ) -> None:
        await self.db.execute(
            delete(FunnelAnswer).where(
                FunnelAnswer.session_id == session.id,
                FunnelAnswer.question_id == question.id,
            )
        )
        self.db.add(
            FunnelAnswer(
                session_id=session.id,
                question_id=question.id,
                option_ids=option_ids,
                value_text=value_text,
                media_file_id=media_file_id,
            )
        )
        await self.db.flush()

    async def _save_contact(
        self, user_id: int, phone: str, account: MessengerAccount
    ) -> None:
        normalized = "+" + re.sub(r"\D", "", phone)
        result = await self.db.execute(
            select(UserContact).where(UserContact.user_id == user_id, UserContact.phone == normalized)
        )
        if result.scalar_one_or_none() is None:
            self.db.add(
                UserContact(
                    user_id=user_id,
                    phone=normalized,
                    first_name=account.first_name,
                    last_name=account.last_name,
                    source="max",
                )
            )
            await self.db.flush()

    async def _summary(self, session: FunnelSession) -> str:
        result = await self.db.execute(
            select(FunnelAnswer, FunnelQuestion)
            .join(FunnelQuestion, FunnelAnswer.question_id == FunnelQuestion.id)
            .where(FunnelAnswer.session_id == session.id)
            .order_by(FunnelQuestion.order)
        )
        lines: list[str] = []
        for answer, question in result.all():
            if question.key in {"photo", "confirmation", "contact"}:
                continue
            value = answer.value_text
            if answer.option_ids:
                options = await self.db.execute(
                    select(FunnelOption.title).where(FunnelOption.id.in_(answer.option_ids))
                )
                value = ", ".join(row[0] for row in options.all())
            if value:
                lines.append(f"{question.title}: {value}")
        return "\n".join(lines) or "Параметры кухни сохранены"

    async def _download_image(self, url: str, session_id: int) -> MediaFile:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        if len(response.content) > self.settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise ValueError("MAX image is too large")
        content_type = response.headers.get("content-type", "image/jpeg").split(";")[0]
        if not content_type.startswith("image/"):
            raise ValueError("MAX attachment is not an image")
        suffix = mimetypes.guess_extension(content_type) or ".jpg"
        directory = Path(self.settings.MEDIA_DIR) / "uploads" / "max" / str(session_id)
        directory.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(response.content).hexdigest()
        path = directory / f"room_{digest[:16]}{suffix}"
        path.write_bytes(response.content)
        media = MediaFile(
            category="room_photo",
            original_filename=path.name,
            stored_path=str(path),
            mime=content_type,
            size_bytes=len(response.content),
            sha256=digest,
        )
        self.db.add(media)
        await self.db.flush()
        return media

    @staticmethod
    def _chat_id(update: dict[str, Any], fallback: str) -> str | int:
        message = update.get("message") or {}
        recipient = message.get("recipient") or {}
        callback = update.get("callback") or {}
        return recipient.get("chat_id") or callback.get("chat_id") or f"user:{fallback}"

    @staticmethod
    def _start_payload(update: dict[str, Any]) -> str:
        return str(update.get("payload") or (update.get("message") or {}).get("body", {}).get("text") or "max")

    @staticmethod
    def _extract_phone(text: str, attachments: list[dict[str, Any]]) -> str | None:
        match = PHONE_RE.search(text)
        if match:
            return match.group(0)
        for attachment in attachments:
            payload = attachment.get("payload") or {}
            candidates = [
                attachment.get("phone"),
                payload.get("phone"),
                (payload.get("contact") or {}).get("phone"),
                (payload.get("max_info") or {}).get("phone"),
                (payload.get("vcf_info") or {}).get("phone"),
            ]
            for candidate in candidates:
                if candidate:
                    return str(candidate)
        return None

    @staticmethod
    def _extract_image_url(attachments: list[dict[str, Any]]) -> str | None:
        for attachment in attachments:
            if attachment.get("type") not in {"image", "photo"}:
                continue
            payload = attachment.get("payload") or {}
            candidates = [attachment.get("url"), payload.get("url")]
            photos = payload.get("photos") or {}
            if isinstance(photos, dict):
                candidates.extend(photos.values())
            for candidate in reversed(candidates):
                if isinstance(candidate, str) and candidate.startswith("http"):
                    return candidate
                if isinstance(candidate, dict) and str(candidate.get("url", "")).startswith("http"):
                    return candidate["url"]
        return None
