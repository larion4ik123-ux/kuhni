# Платформа «Мебельный салон Интерьер»

Платформа для Артёма Ермакова и компании «Интерьер»: публичный сайт, MAX-бот с воронкой подбора кухни, визуализация по фотографии помещения, админпанель и система заявок.

## Состав монорепозитория

```
frontend/   Публичный статический сайт (Vite → dist)
backend/    FastAPI: API, MAX webhook, сервисы, провайдеры, модели
bot/        MAX Bot API: транспорт, сценарий и регистрация webhook
worker/     Фоновые задачи: AI-генерация и рассылки (polling таблицы jobs)
shared/     Общие константы, enum, схемы
assets/     Материалы клиента (raw — оригиналы, processed — варианты)
scripts/    Подготовка изображений, плейсхолдеры, утилиты
docs/       Архитектура, БД, воронка, развёртывание, контент
deploy/     Конфиги Nginx и systemd
tests/      Тесты
```

## Архитектурный принцип

Бизнес-логика живёт в `backend/app/services` и **мессенджер-независима**.
MAX работает через официальный HTTPS webhook. Сценарий сохраняется в SQLite,
поэтому перезапуск сервера не сбрасывает ответы пользователя.

AI-генерация подключается через интерфейс `ImageGenerationProvider`
(`backend/app/providers/`): `MockGenerationProvider` (для разработки) и
`OpenAICompatibleGenerationProvider` (polza.ai). Провайдер меняется в настройках.

## Схема запуска

Сайт можно разместить на GitHub Pages для демонстрации или на VPS. Рабочий
MAX-бот подключается к VPS через HTTPS webhook после выдачи токена MAX.

## Быстрый старт (разработка)

```bash
# 1. Окружение
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Конфиг
cp .env.example .env  # заполнить SECRET_KEY, токены

# 3. Подготовить изображения (плейсхолдеры + обработка)
python scripts/generate_placeholders.py
python scripts/process_images.py

# 4. Миграции и seed-данные
alembic upgrade head

# 5. Запуск
uvicorn backend.app.main:app --reload          # API + админка
python -m bot.main                              # проверка токена MAX
python -m bot.main --register-webhook           # регистрация webhook MAX
python worker/generation_worker.py              # worker генерации
python worker/broadcast_worker.py               # worker рассылок

# Frontend
cd frontend && npm install && npm run dev
```

## Документация

- `docs/ARCHITECTURE.md` — архитектура и разделение слоёв
- `docs/DATABASE.md` — модели данных
- `docs/FUNNEL.md` — настраиваемая воронка
- `docs/DEPLOYMENT.md` — развёртывание (GitHub Pages + VPS, затем VPS + Nginx)
- `docs/CONTENT.md` / `docs/CONTENT_REQUIRED.md` — материалы и недостающие данные
- `TASKS.md` — план работ и статус

## Ограничения проекта

- Бот не сообщает точную стоимость: он собирает проект и передаёт заявку Артёму.
- Реальные фотографии клиента — основа сайта; AI-визуализации не выдаются за реальные работы.
- Отзывы — только реальные, со ссылкой на источник; без выдуманных данных.
- Стек рассчитан на сервер с 1 ГБ RAM: без Redis/Kubernetes/Node.js в production.
