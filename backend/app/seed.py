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

# ───────────────────────── Данные воронки ─────────────────────────

FUNNEL_QUESTIONS = [
    {"key": "form", "title": "Какая планировка нужна?", "description": "Выберите ближайший вариант. Точные размеры уточним на замере.", "type": "single_choice", "order": 1, "required": True, "active": True, "generation_key": "form"},
    {"key": "width", "title": "Примерная ширина рабочей зоны", "description": "Напишите в сантиметрах, например: 320 см.", "type": "text", "order": 2, "required": True, "active": True, "generation_key": "width"},
    {"key": "height", "title": "Высота помещения", "description": "Напишите в сантиметрах, например: 265 см.", "type": "text", "order": 3, "required": True, "active": True, "generation_key": "height"},
    {"key": "area", "title": "Примерная площадь кухни", "description": "Напишите в квадратных метрах, например: 12 м².", "type": "text", "order": 4, "required": True, "active": True, "generation_key": "area"},
    {"key": "style", "title": "Какой характер кухни вам ближе?", "type": "single_choice", "order": 5, "required": True, "active": True, "generation_key": "style"},
    {"key": "color", "title": "Какая цветовая гамма нравится?", "type": "single_choice", "order": 6, "required": True, "active": True, "generation_key": "color"},
    {"key": "handle", "title": "Как открывать фасады?", "type": "single_choice", "order": 7, "required": True, "active": True, "generation_key": "handle"},
    {"key": "appliances", "title": "Какая техника должна быть встроена?", "description": "Например: холодильник, духовка, посудомоечная машина, вытяжка.", "type": "text", "order": 8, "required": True, "active": True, "generation_key": "appliances"},
    {"key": "wishes", "title": "Что ещё важно учесть?", "description": "Например: больше хранения, место для микроволновки или рабочая зона у окна.", "type": "text", "order": 9, "required": False, "active": True, "generation_key": "wishes"},
    {"key": "photo", "title": "Теперь пришлите фото помещения", "description": "Снимите комнату целиком: пусть в кадре будут видны стены, пол, потолок, окна и двери.", "type": "photo", "order": 10, "required": True, "active": True},
    {"key": "contact", "title": "Куда Артёму написать по вашему проекту?", "description": "Отправьте номер кнопкой MAX. Бот не рассчитывает цену — заявку посмотрит Артём лично.", "type": "contact", "order": 11, "required": True, "active": True},
    {"key": "confirmation", "title": "Проверьте, всё ли верно", "type": "confirmation", "order": 12, "required": True, "active": True},
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
        {"title": "Светлая", "internal_code": "light", "generation_hint": "Светлая спокойная гамма фасадов", "order": 1},
        {"title": "Графитовая", "internal_code": "graphite", "generation_hint": "Графитовые фасады без синего оттенка", "order": 2},
        {"title": "Под дерево", "internal_code": "wood", "generation_hint": "Натуральная древесная фактура", "order": 3},
        {"title": "Цветной акцент", "internal_code": "accent", "generation_hint": "Один сдержанный цветной акцент в фасадах", "order": 4},
    ],
    "handle": [
        {"title": "Без ручек / Gola", "internal_code": "gola", "generation_hint": "Фасады без накладных ручек, профиль Gola", "order": 1},
        {"title": "Лаконичные ручки", "internal_code": "slim", "generation_hint": "Тонкие лаконичные накладные ручки", "order": 2},
        {"title": "Классические ручки", "internal_code": "classic_handle", "generation_hint": "Аккуратные классические ручки", "order": 3},
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
    {"key": "contacts_max", "title": "MAX", "content": "", "order": 9},
    {"key": "contacts_address", "title": "Адрес", "content": "—", "order": 10},
    {"key": "contacts_region", "title": "Регион", "content": "—", "order": 11},
    {"key": "contacts_hours", "title": "Режим работы", "content": "Пн-Пт: 9:00-18:00", "order": 12},
    {"key": "yandex_maps_url", "title": "Яндекс.Карты", "content": "", "order": 13},
    {"key": "yandex_widget_html", "title": "Виджет Яндекс", "content": "", "order": 14},
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
        existing = FunnelQuestion(**data)
        db.add(existing)
        await db.flush()
    else:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)
    active_codes: set[str] = set()
    for opt in FUNNEL_OPTIONS.get(data["key"], []):
        active_codes.add(opt["internal_code"])
        result = await db.execute(
            select(FunnelOption).where(
                FunnelOption.question_id == existing.id,
                FunnelOption.internal_code == opt["internal_code"],
            )
        )
        option = result.scalar_one_or_none()
        if option is None:
            option = FunnelOption(question_id=existing.id, **opt)
        else:
            for key, value in opt.items():
                setattr(option, key, value)
        option.active = True
        db.add(option)
    stale = await db.execute(select(FunnelOption).where(FunnelOption.question_id == existing.id))
    for option in stale.scalars():
        if option.internal_code not in active_codes:
            option.active = False
            db.add(option)


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

        # Preserve historical answers but prevent retired questions from
        # reappearing in the current customer journey after a reseed.
        active_keys = {question["key"] for question in FUNNEL_QUESTIONS}
        stale_questions = await db.execute(
            select(FunnelQuestion).where(
                FunnelQuestion.active.is_(True), FunnelQuestion.key.not_in(active_keys)
            )
        )
        for question in stale_questions.scalars():
            question.active = False
            db.add(question)

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
