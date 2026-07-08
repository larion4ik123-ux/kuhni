"""Идемпотентный seed: вопросы воронки, опции, материалы, блоки сайта, админ.

Запуск: python -m backend.app.seed
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.core.security import hash_password
from backend.app.core.settings import get_settings
from backend.app.models import (
    Admin,
    FAQItem,
    FunnelOption,
    FunnelQuestion,
    ProcessStep,
    SiteBlock,
)

# ───────────────────────── Данные воронки (16 шагов) ─────────────────────────

FUNNEL_QUESTIONS = [
    # 1
    {"key": "welcome", "title": "Я Артём. Давайте соберём кухню под ваше помещение: форма, стиль, материалы и фото для визуализации.", "type": "text", "order": 1, "required": False, "active": True, "allow_skip": True},
    # 2
    {"key": "form", "title": "Какая форма кухни вам нужна?", "type": "single_choice", "order": 2, "required": True, "active": True, "generation_key": "form"},
    # 3
    {"key": "style", "title": "Какой стиль предпочитаете?", "type": "single_choice", "order": 3, "required": True, "active": True, "generation_key": "style"},
    # 4
    {"key": "color", "title": "Какой цвет фасадов?", "type": "single_choice", "order": 4, "required": True, "active": True, "generation_key": "color"},
    # 5
    {"key": "facade", "title": "Материал фасада", "type": "single_choice", "order": 5, "required": True, "active": True, "generation_key": "facade"},
    # 6
    {"key": "handle", "title": "Ручки / система открывания", "type": "single_choice", "order": 6, "required": True, "active": True, "generation_key": "handle"},
    # 7
    {"key": "countertop", "title": "Столешница", "type": "single_choice", "order": 7, "required": False, "active": False, "generation_key": "countertop"},
    # 8
    {"key": "hardware", "title": "Фурнитура", "type": "single_choice", "order": 8, "required": False, "active": False, "generation_key": "hardware"},
    # 9
    {"key": "size", "title": "Напишите примерный размер или площадь помещения", "type": "text", "order": 9, "required": True, "active": True, "generation_key": "size"},
    # 10
    {"key": "deadline", "title": "Желаемый срок изготовления", "type": "text", "order": 10, "required": True, "active": True},
    # 11
    {"key": "budget", "title": "Примерный бюджет", "type": "text", "order": 11, "required": False, "active": False, "allow_skip": True},
    # 12
    {"key": "wishes", "title": "Дополнительные пожелания", "type": "text", "order": 12, "required": False, "active": True, "allow_skip": True, "generation_key": "wishes"},
    # 13
    {"key": "room_type", "title": "Тип исходного помещения", "type": "single_choice", "order": 13, "required": True, "active": True, "generation_key": "room_type"},
    # 14
    {"key": "photo", "title": "Пришлите фото помещения: по нему бот подготовит основу для визуализации кухни в вашем интерьере", "type": "photo", "order": 14, "required": True, "active": True},
    # 15
    {"key": "confirmation", "title": "Проверьте подбор. Если всё верно, бот передаст заявку администратору.", "type": "confirmation", "order": 15, "required": True, "active": True},
    # 16
    {"key": "contact", "title": "Оставьте номер, чтобы Артём связал подбор с вами", "type": "contact", "order": 16, "required": True, "active": True},
]

FUNNEL_OPTIONS = {
    "form": [
        {"title": "Прямая", "internal_code": "straight", "generation_hint": "Прямая линейная кухня вдоль одной стены", "order": 1},
        {"title": "Угловая", "internal_code": "corner", "generation_hint": "Угловая кухня с рабочей зоной вдоль двух смежных стен", "order": 2},
        {"title": "П-образная", "internal_code": "u_shape", "generation_hint": "П-образная кухня с рабочей зоной по трём стенам", "order": 3},
        {"title": "С островом", "internal_code": "island", "generation_hint": "Кухня с отдельным островом в центре помещения", "order": 4},
    ],
    "style": [
        {"title": "Современный", "internal_code": "modern", "generation_hint": "Современная кухня с чистыми геометрическими линиями, гладкими фасадами, минимальным декором", "order": 1},
        {"title": "Неоклассика", "internal_code": "neoclassic", "generation_hint": "Неоклассическая кухня с элегантными деталями, мягкими цветами, современным комфортом", "order": 2},
        {"title": "Классика", "internal_code": "classic", "generation_hint": "Классическая кухня с филенчатыми фасадами, декоративными элементами, тёплыми тонами", "order": 3},
    ],
    "color": [
        {"title": "Серый", "internal_code": "gray", "generation_hint": "Серые фасады", "order": 1},
        {"title": "Бежевый", "internal_code": "beige", "generation_hint": "Бежевые фасады", "order": 2},
        {"title": "Зелёный", "internal_code": "green", "generation_hint": "Зелёные фасады", "order": 3},
        {"title": "Белый", "internal_code": "white", "generation_hint": "Белые фасады", "order": 4},
    ],
    "facade": [
        {"title": "Interno", "internal_code": "interno", "generation_hint": "Фасады Interno", "order": 1},
        {"title": "AGT", "internal_code": "agt", "generation_hint": "Фасады AGT", "order": 2},
        {"title": "Egger", "internal_code": "egger", "generation_hint": "Фасады Egger", "order": 3},
        {"title": "Kronospan", "internal_code": "kronospan", "generation_hint": "Фасады Kronospan", "order": 4},
    ],
    "handle": [
        {"title": "Скоба", "internal_code": "handle", "generation_hint": "Скобчатые ручки", "order": 1},
        {"title": "Чёрная квадратная", "internal_code": "black_square", "generation_hint": "Чёрные квадратные ручки", "order": 2},
        {"title": "Кнопка", "internal_code": "knob", "generation_hint": "Кнопочные ручки", "order": 3},
        {"title": "Профиль Gola", "internal_code": "gola", "generation_hint": "Система открывания профиль Gola (без ручек)", "order": 4},
    ],
    "countertop": [
        {"title": "Кварцевый агломерат", "internal_code": "quartz", "generation_hint": "Кварцевая столешница", "order": 1},
        {"title": "Акриловый камень", "internal_code": "acrylic", "generation_hint": "Акриловая столешница", "order": 2},
        {"title": "ДСП ламинированное", "internal_code": "dsp", "generation_hint": "Ламинированная столешница", "order": 3},
    ],
    "hardware": [
        {"title": "Blum", "internal_code": "blum", "generation_hint": "Фурнитура Blum", "order": 1},
        {"title": "Hettich", "internal_code": "hettich", "generation_hint": "Фурнитура Hettich", "order": 2},
        {"title": "Grass", "internal_code": "grass", "generation_hint": "Фурнитура Grass", "order": 3},
    ],
    "room_type": [
        {"title": "Пустое помещение", "internal_code": "empty", "generation_hint": "Пустое помещение без мебели", "order": 1},
        {"title": "Старая кухня", "internal_code": "old_kitchen", "generation_hint": "Помещение со старой кухней, которую нужно заменить", "order": 2},
    ],
}

# ───────────────────────── Блоки сайта ─────────────────────────

SITE_BLOCKS = [
    {"key": "hero_title", "title": "Главный экран", "content": "Я Артём. Соберу кухню под ваш дом.", "order": 1},
    {"key": "hero_subtitle", "title": "", "content": "Лично разбираю планировку, материалы и бюджет, а команда изготавливает и монтирует кухню под размеры вашего помещения.", "order": 2},
    {"key": "advantages_title", "title": "Почему выбирают нас", "content": "", "order": 3},
    {"key": "advantage_1", "title": "Личный контроль", "content": "Артём сам смотрит заявку, планировку и нюансы помещения.", "order": 4},
    {"key": "advantage_2", "title": "Реальные работы", "content": "На сайте показаны фотографии кухонь из текущей папки проекта.", "order": 5},
    {"key": "advantage_3", "title": "Подбор в MAX", "content": "Бот собирает стиль, форму, материалы и фото для визуализации.", "order": 6},
    {"key": "about", "title": "Личная работа Артёма", "content": "Не безликий салон: Артём лично ведёт проект, смотрит размеры, технику, материалы и бюджет, а команда помогает с производством и монтажом.", "order": 7},
    {"key": "contacts_phone", "title": "Телефон", "content": "+7 (XXX) XXX-XX-XX", "order": 8},
    {"key": "contacts_telegram", "title": "Telegram", "content": "https://t.me/your_bot", "order": 9},
    {"key": "contacts_max", "title": "MAX", "content": "", "order": 10},
    {"key": "contacts_address", "title": "Адрес", "content": "—", "order": 11},
    {"key": "contacts_region", "title": "Регион", "content": "—", "order": 12},
    {"key": "contacts_hours", "title": "Режим работы", "content": "Пн-Пт: 9:00-18:00", "order": 13},
    {"key": "yandex_maps_url", "title": "Яндекс.Карты", "content": "", "order": 14},
    {"key": "yandex_widget_html", "title": "Виджет Яндекс", "content": "", "order": 15},
]

# ───────────────────────── Этапы работы ─────────────────────────

PROCESS_STEPS = [
    {"step_number": 1, "title": "Подбор", "description": "Вы отвечаете на короткие вопросы в боте.", "display_order": 1},
    {"step_number": 2, "title": "Визуализация", "description": "Бот собирает вводные и готовит изображение будущей кухни по фото помещения.", "display_order": 2},
    {"step_number": 3, "title": "Разбор заявки", "description": "Артём смотрит планировку, материалы, технику и нюансы помещения.", "display_order": 3},
    {"step_number": 4, "title": "Замер", "description": "Уточняем размеры, выводы, розетки, газ, воду и технику.", "display_order": 4},
    {"step_number": 5, "title": "Изготовление", "description": "Изготавливаем кухню под согласованный проект.", "display_order": 5},
    {"step_number": 6, "title": "Монтаж", "description": "Привозим, собираем и сдаём готовую кухню.", "display_order": 6},
]

# ───────────────────────── FAQ ─────────────────────────

FAQ_ITEMS = [
    {"question": "Что делает бот MAX?", "answer": "Бот собирает форму кухни, стиль, цвет, материалы и фото помещения, чтобы Артём сразу видел цельную заявку.", "display_order": 1},
    {"question": "Будет ли визуализация по моему фото?", "answer": "Да. Визуализация помогает увидеть идею кухни в вашем интерьере, но не заменяет рабочий чертёж и точный замер.", "display_order": 2},
    {"question": "Назовёт ли бот точную цену?", "answer": "Нет. Бот собирает вводные и передаёт заявку администратору. После просмотра заявки менеджер свяжется с вами и согласует следующий шаг.", "display_order": 3},
    {"question": "Какие материалы используете?", "answer": "Работаем с фасадами Interno, AGT, Egger, Kronospan; фурнитурой Blum, Hettich, Grass; столешницами из кварца и акрилового камня.", "display_order": 4},
]


async def _upsert_question(db: AsyncSession, data: dict) -> None:
    """Upsert вопроса воронки по key."""
    result = await db.execute(select(FunnelQuestion).where(FunnelQuestion.key == data["key"]))
    existing = result.scalar_one_or_none()
    if existing is None:
        obj = FunnelQuestion(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        # Добавляем опции
        for opt in FUNNEL_OPTIONS.get(data["key"], []):
            option = FunnelOption(
                question_id=obj.id,
                title=opt["title"],
                internal_code=opt["internal_code"],
                generation_hint=opt.get("generation_hint"),
                order=opt["order"],
            )
            db.add(option)
    else:
        # Обновляем только если нужно
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)


async def _upsert_site_block(db: AsyncSession, data: dict) -> None:
    """Upsert блока сайта по key."""
    result = await db.execute(select(SiteBlock).where(SiteBlock.key == data["key"]))
    existing = result.scalar_one_or_none()
    if existing is None:
        db.add(SiteBlock(**data))
    else:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)


async def _upsert_faq(db: AsyncSession, data: dict) -> None:
    """Upsert FAQ."""
    result = await db.execute(
        select(FAQItem).where(FAQItem.question == data["question"])
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        db.add(FAQItem(**data))
    else:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)


async def _upsert_process_step(db: AsyncSession, data: dict) -> None:
    """Upsert этапа работы."""
    result = await db.execute(
        select(ProcessStep).where(ProcessStep.step_number == data["step_number"])
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        db.add(ProcessStep(**data))
    else:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)


async def _upsert_admin(db: AsyncSession) -> None:
    """Создаёт администратора по умолчанию из настроек (bcrypt-хеш)."""
    settings = get_settings()
    result = await db.execute(select(Admin).where(Admin.username == settings.ADMIN_DEFAULT_USERNAME))
    existing = result.scalar_one_or_none()
    if existing is None:
        admin = Admin(
            username=settings.ADMIN_DEFAULT_USERNAME,
            password_hash=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
            is_active=True,
        )
        db.add(admin)
    else:
        # Обновляем пароль, если изменился в .env
        existing.password_hash = hash_password(settings.ADMIN_DEFAULT_PASSWORD)
        db.add(existing)


async def seed() -> None:
    """Главная функция seed."""
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as db:
        # Вопросы воронки
        for q in FUNNEL_QUESTIONS:
            await _upsert_question(db, q)

        # Блоки сайта
        for b in SITE_BLOCKS:
            await _upsert_site_block(db, b)

        # FAQ
        for f in FAQ_ITEMS:
            await _upsert_faq(db, f)

        # Этапы работы
        for s in PROCESS_STEPS:
            await _upsert_process_step(db, s)

        # Админ
        await _upsert_admin(db)

        await db.commit()
        print("Seed завершён: вопросы, опции, блоки, FAQ, этапы, админ.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
