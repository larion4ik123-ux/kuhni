# Платформа «Мебельный салон Интерьер»

Полноценная платформа для компании по изготовлению кухонь на заказ: публичный сайт, Telegram-бот с настраиваемой воронкой подбора, AI-визуализация кухни по фотографии помещения, веб-админпанель, система заявок и рассылок.

## Состав монорепозитория

```
frontend/   Публичный статический сайт (Vite → dist)
backend/    FastAPI: API, админпанель (Jinja2+HTMX), сервисы, провайдеры, модели
bot/        Telegram-адаптер (aiogram 3.x) + заглушка MAX-адаптера
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
Telegram — это адаптер, реализующий интерфейс `MessengerAdapter`
(`bot/adapters/`). Это позволяет на этапе 2 заменить/дополнить Telegram на MAX
через `MaxAdapter` без переписывания воронки, заявок и генерации.

AI-генерация подключается через интерфейс `ImageGenerationProvider`
(`backend/app/providers/`): `MockGenerationProvider` (для разработки) и
`OpenAICompatibleGenerationProvider` (polza.ai). Провайдер меняется в настройках.

## Схема запуска

**Этап 1** — публичный сайт на GitHub Pages, остальное на VPS (Ubuntu 24.04,
1 CPU / 1 ГБ RAM / 20 ГБ). Витрина говорит про MAX-бот, но ссылку можно
временно направить в Telegram через `VITE_MAX_BOT_URL`.

**Этап 2** — перенос сайта на VPS за Nginx, свой домен; Telegram заменяется или
дополняется MAX без переписывания бизнес-логики.

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
python -m bot.main                              # Telegram-бот (polling)
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

- Генерация запускается **только после передачи контакта**.
- Реальные фотографии клиента — основа сайта; AI-визуализации не выдаются за реальные работы.
- Отзывы — только реальные, со ссылкой на источник; без выдуманных данных.
- Стек рассчитан на сервер с 1 ГБ RAM: без Redis/Kubernetes/Node.js в production.
