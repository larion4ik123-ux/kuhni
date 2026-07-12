"""Telegram funnel handlers.

The handler is intentionally thin: it maps Telegram events into messenger-neutral
services and keeps the critical generation rule in GenerationService.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.settings import get_settings
from backend.app.models import (
    FunnelOption,
    FunnelQuestion,
    FunnelSession,
    Lead,
    MediaFile,
    MessengerAccount,
    User,
    UserContact,
)
from backend.app.repositories.repos import (
    FunnelAnswerRepository,
    FunnelQuestionRepository,
    GenerationJobRepository,
    JobRepository,
    LeadRepository,
    LeadStatusHistoryRepository,
)
from backend.app.services.funnel import FunnelService
from backend.app.services.generation import GenerationService
from backend.app.services.lead import LeadService
from backend.app.services.notify import NotifyService
from bot.adapters import MessengerButton, TelegramAdapter
from bot.keyboards.funnel import option_buttons
from bot.states.funnel import FunnelStates
from shared.schemas import AnswerPayload

router = Router(name="telegram_funnel")
logger = logging.getLogger(__name__)


def _sent_message_id(sent_message: object) -> int | None:
    message_id = getattr(sent_message, "message_id", None)
    if message_id is None:
        return None
    return int(message_id)


async def _remember_cleanup_message(state: FSMContext, sent_message: object | None) -> None:
    message_id = _sent_message_id(sent_message)
    if message_id is not None:
        await state.update_data(cleanup_message_ids=[message_id])


async def _delete_message_safely(bot: object, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:  # noqa: BLE001
        logger.debug("Could not delete Telegram message %s in chat %s", message_id, chat_id, exc_info=True)


async def _cleanup_step_messages(message: Message, state: FSMContext, *, delete_user_message: bool) -> None:
    """Keep the briefing history intact and avoid inconsistent deletions."""
    del message, state, delete_user_message


def _callback_chat_id(callback: CallbackQuery) -> int:
    if callback.message and getattr(callback.message, "chat", None):
        return int(callback.message.chat.id)
    return int(callback.from_user.id)


async def _delete_callback_message(callback: CallbackQuery) -> None:
    """Keep the chosen option in the chat instead of deleting only part of it."""
    del callback


async def _ensure_account(db: AsyncSession, telegram_user: TelegramUser) -> MessengerAccount:
    result = await db.execute(
        select(MessengerAccount).where(
            MessengerAccount.messenger == "telegram",
            MessengerAccount.account_id == str(telegram_user.id),
        )
    )
    account = result.scalar_one_or_none()
    if account is not None:
        account.username = telegram_user.username
        account.first_name = telegram_user.first_name
        account.last_name = telegram_user.last_name
        return account

    user = User()
    db.add(user)
    await db.flush()
    account = MessengerAccount(
        user_id=user.id,
        messenger="telegram",
        account_id=str(telegram_user.id),
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


async def _create_session(db: AsyncSession, account: MessengerAccount, source: str) -> FunnelSession:
    session = FunnelSession(
        user_id=account.user_id,
        messenger_account_id=account.id,
        status="in_progress",
        source=source or "organic",
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def _funnel_service(db: AsyncSession) -> FunnelService:
    return FunnelService(
        db,
        FunnelQuestionRepository(db),
        FunnelAnswerRepository(db),
    )


async def _send_question(
    db: AsyncSession,
    adapter: TelegramAdapter,
    chat_id: int,
    session: FunnelSession,
    question: FunnelQuestion | None,
    state: FSMContext,
) -> None:
    if question is None:
        await _finalize_session(db, adapter, chat_id, session, state)
        return

    session.current_question_id = question.id
    db.add(session)
    await db.flush()

    if question.key == "welcome":
        await adapter.send_text(chat_id, question.title)
        service = await _funnel_service(db)
        next_question = await service.get_next_question(session, question)
        await _send_question(db, adapter, chat_id, session, next_question, state)
        return

    if question.type == "single_choice":
        result = await db.execute(
            select(FunnelOption)
            .where(FunnelOption.question_id == question.id, FunnelOption.active.is_(True))
            .order_by(FunnelOption.order)
        )
        options = list(result.scalars().all())
        await adapter.send_buttons(
            chat_id,
            question.title,
            option_buttons(session.id, question.id, options),
        )
        await state.clear()
        return

    if question.type == "photo":
        sent = await adapter.send_text(chat_id, question.title)
        await state.set_state(FunnelStates.waiting_photo)
        await state.update_data(session_id=session.id, question_id=question.id)
        await _remember_cleanup_message(state, sent)
        return

    if question.type == "contact":
        sent = await adapter.request_contact(
            chat_id,
            "Оставьте номер для связи по вашему проекту. Артём получит собранную заявку и свяжется с вами.",
        )
        await state.set_state(FunnelStates.waiting_contact)
        await state.update_data(session_id=session.id, question_id=question.id)
        await _remember_cleanup_message(state, sent)
        return

    if question.type == "confirmation":
        buttons = [
            MessengerButton("Подтвердить выбор", f"funnel:confirm:{session.id}:{question.id}"),
            MessengerButton("Начать заново", f"funnel:restart:{session.id}"),
        ]
        await adapter.send_buttons(
            chat_id,
            "Проверьте подбор. Если всё верно, передам заявку администратору.",
            buttons,
        )
        await state.clear()
        return

    sent = await adapter.send_text(chat_id, question.title)
    await state.set_state(FunnelStates.waiting_text)
    await state.update_data(session_id=session.id, question_id=question.id)
    await _remember_cleanup_message(state, sent)


async def _finalize_session(
    db: AsyncSession,
    adapter: TelegramAdapter,
    chat_id: int,
    session: FunnelSession,
    state: FSMContext,
) -> None:
    """Create one completed lead only after the complete brief is confirmed."""
    if session.status == "completed":
        await adapter.send_text(chat_id, "Этот подбор уже передан Артёму.")
        await state.clear()
        return

    settings = get_settings()
    gen_service = GenerationService(db, GenerationJobRepository(db), JobRepository(db), settings)
    selection = gen_service.build_selection_summary(await gen_service._get_session_answers(session.id))
    lead_service = LeadService(db, LeadRepository(db), LeadStatusHistoryRepository(db))
    lead = await lead_service.create_lead_from_session(
        session_id=session.id,
        user_id=session.user_id,
        source=session.source,
        selection_description=selection.text,
    )

    manager_notified = False
    if isinstance(lead, Lead) and settings.MANAGER_CHAT_IDS:
        try:
            await NotifyService(adapter, settings.MANAGER_CHAT_IDS).notify_new_lead(lead)
            manager_notified = True
        except Exception:  # noqa: BLE001
            logger.exception("Could not notify managers about lead %s", lead.id)

    generation = await gen_service.create_job(
        lead_id=lead.id if isinstance(lead, Lead) else None,
        session_id=session.id,
        user_id=session.user_id,
    )
    session.status = "completed"
    db.add(session)
    await db.flush()
    await state.clear()

    status = "Заявка передана Артёму." if manager_notified else "Заявка сохранена для Артёма."
    visual = " Визуальный вариант поставлен в очередь." if generation else ""
    await adapter.send_text(
        chat_id,
        f"Готово! {status} Он увидит размеры, подбор и фото помещения и свяжется с вами.{visual}",
        reply_markup=ReplyKeyboardRemove(),
    )


def _source_from_start(message: Message) -> str:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 2:
        return parts[1].strip() or "organic"
    return "organic"


@router.message(F.text.startswith("/start"))
async def start(message: Message, db: AsyncSession, state: FSMContext) -> None:
    adapter = TelegramAdapter(message.bot)
    account = await _ensure_account(db, message.from_user)
    session = await _create_session(db, account, _source_from_start(message))
    service = await _funnel_service(db)
    first = await service.get_next_question(session, None)
    await adapter.send_text(
        message.chat.id,
        "Здравствуйте! Я Артём. Давайте спокойно соберём будущую кухню: размеры, планировку, стиль, материалы и фото помещения.",
    )
    await _send_question(db, adapter, message.chat.id, session, first, state)


@router.callback_query(F.data.startswith("funnel:opt:"))
async def option_selected(callback: CallbackQuery, db: AsyncSession, state: FSMContext) -> None:
    adapter = TelegramAdapter(callback.bot)
    _, _, session_id_raw, question_id_raw, option_id_raw = callback.data.split(":")
    session = await db.get(FunnelSession, int(session_id_raw))
    question = await db.get(FunnelQuestion, int(question_id_raw))
    if session is None or question is None:
        await adapter.answer_callback(callback.id, "Сессия не найдена")
        return

    service = await _funnel_service(db)
    await service.save_answer(
        session,
        AnswerPayload(question_id=question.id, option_ids=[int(option_id_raw)]),
    )
    await adapter.answer_callback(callback.id)
    chat_id = _callback_chat_id(callback)
    await _delete_callback_message(callback)
    next_question = await service.get_next_question(session, question)
    await _send_question(db, adapter, chat_id, session, next_question, state)


@router.callback_query(F.data.startswith("funnel:confirm:"))
async def confirm_selected(callback: CallbackQuery, db: AsyncSession, state: FSMContext) -> None:
    adapter = TelegramAdapter(callback.bot)
    _, _, session_id_raw, question_id_raw = callback.data.split(":")
    session = await db.get(FunnelSession, int(session_id_raw))
    question = await db.get(FunnelQuestion, int(question_id_raw))
    if session is None or question is None:
        await adapter.answer_callback(callback.id, "Сессия не найдена")
        return

    service = await _funnel_service(db)
    await service.save_answer(session, AnswerPayload(question_id=question.id, value_text="confirmed"))
    await adapter.answer_callback(callback.id)
    chat_id = _callback_chat_id(callback)
    await _delete_callback_message(callback)
    next_question = await service.get_next_question(session, question)
    await _send_question(db, adapter, chat_id, session, next_question, state)


@router.callback_query(F.data.startswith("funnel:restart:"))
async def restart_selected(callback: CallbackQuery, db: AsyncSession, state: FSMContext) -> None:
    adapter = TelegramAdapter(callback.bot)
    account = await _ensure_account(db, callback.from_user)
    session = await _create_session(db, account, "telegram_restart")
    service = await _funnel_service(db)
    await adapter.answer_callback(callback.id)
    chat_id = _callback_chat_id(callback)
    await _delete_callback_message(callback)
    await _send_question(db, adapter, chat_id, session, await service.get_next_question(session, None), state)


@router.message(FunnelStates.waiting_text)
async def text_answer(message: Message, db: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    session = await db.get(FunnelSession, int(data["session_id"]))
    question = await db.get(FunnelQuestion, int(data["question_id"]))
    if session is None or question is None:
        await state.clear()
        await message.answer("Сессия не найдена. Нажмите /start, чтобы начать заново.")
        return
    service = await _funnel_service(db)
    await service.save_answer(session, AnswerPayload(question_id=question.id, value_text=message.text))
    await _cleanup_step_messages(message, state, delete_user_message=True)
    await state.clear()
    await _send_question(db, TelegramAdapter(message.bot), message.chat.id, session, await service.get_next_question(session, question), state)


@router.message(FunnelStates.waiting_photo, F.photo)
async def photo_answer(message: Message, db: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    session = await db.get(FunnelSession, int(data["session_id"]))
    question = await db.get(FunnelQuestion, int(data["question_id"]))
    if session is None or question is None:
        await state.clear()
        await message.answer("Сессия не найдена. Нажмите /start, чтобы начать заново.")
        return
    photo = message.photo[-1]
    settings = get_settings()
    stored_path = f"telegram:{photo.file_id}"
    try:
        media_dir = Path(settings.MEDIA_DIR) / "user_rooms"
        media_dir.mkdir(parents=True, exist_ok=True)
        safe_unique = "".join(ch for ch in photo.file_unique_id if ch.isalnum() or ch in ("-", "_"))
        out_path = (media_dir / f"session_{session.id}_{safe_unique}.jpg").resolve()
        telegram_file = await message.bot.get_file(photo.file_id)
        if telegram_file.file_path:
            with out_path.open("wb") as destination:
                await message.bot.download_file(telegram_file.file_path, destination=destination)
            stored_path = str(out_path)
    except Exception:  # noqa: BLE001
        logger.exception("Could not download Telegram room photo, keeping file_id fallback")

    media = MediaFile(
        category="user_room",
        original_filename=f"telegram_{photo.file_unique_id}.jpg",
        stored_path=stored_path,
        mime="image/jpeg",
        width=photo.width,
        height=photo.height,
        size_bytes=photo.file_size,
        is_real_work=False,
    )
    db.add(media)
    await db.flush()
    service = await _funnel_service(db)
    await service.save_answer(session, AnswerPayload(question_id=question.id, media_file_id=media.id))
    await _cleanup_step_messages(message, state, delete_user_message=True)
    await state.clear()
    await _send_question(db, TelegramAdapter(message.bot), message.chat.id, session, await service.get_next_question(session, question), state)


@router.message(FunnelStates.waiting_contact, F.contact)
async def contact_answer(message: Message, db: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    session = await db.get(FunnelSession, int(data["session_id"]))
    question_id = int(data.get("question_id") or 0)
    if session is None:
        await state.clear()
        await message.answer("Сессия не найдена. Нажмите /start, чтобы начать заново.")
        return

    contact = message.contact
    db.add(
        UserContact(
            user_id=session.user_id,
            phone=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name,
            source=session.source,
        )
    )
    if question_id:
        service = await _funnel_service(db)
        await service.save_answer(
            session,
            AnswerPayload(
                question_id=question_id,
                phone=contact.phone_number,
                first_name=contact.first_name,
                last_name=contact.last_name,
                value_text=contact.phone_number,
            ),
        )

    await _cleanup_step_messages(message, state, delete_user_message=True)
    await state.clear()
    question = await db.get(FunnelQuestion, question_id) if question_id else None
    service = await _funnel_service(db)
    await _send_question(
        db,
        TelegramAdapter(message.bot),
        message.chat.id,
        session,
        await service.get_next_question(session, question),
        state,
    )
