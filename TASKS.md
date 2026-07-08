# TASKS — план работ

Статус: `[ ]` pending · `[~]` in_progress · `[x]` done · `[!]` blocked

## Этап 0 — подготовка
- [x] Инициализация монорепозитория, структура директорий, git
- [x] Базовые файлы: .gitignore, .env.example, pyproject.toml, README.md
- [~] Документация: ARCHITECTURE.md, DATABASE.md, FUNNEL.md, DEPLOYMENT.md, CONTENT.md, CONTENT_REQUIRED.md
- [~] Placeholder-изображения (scripts/generate_placeholders.py)
- [x] Скрипт обработки изображений (scripts/process_images.py) + assets-manifest.json

## Этап 1 — backend-ядро
- [x] shared/: enum (QuestionType, LeadStatus, JobType, MessengerType, ...), константы, общие Pydantic-схемы
- [x] backend/app/models/: все модели SQLAlchemy 2 (см. DATABASE.md)
- [~] backend/app/core/: settings (pydantic-settings), database (async engine, WAL), security (bcrypt, сессии, CSRF), deps
- [x] Alembic: начальная миграция
- [x] backend/app/seed.py: вопросы воронки, варианты (generation_hint), материалы, блоки сайта, FAQ, этапы
- [x] backend/app/repositories/: доступ к данным (session/lead/gallery/review/...)
- [x] backend/app/providers/: ImageGenerationProvider, MockGenerationProvider, OpenAICompatibleGenerationProvider (polza.ai: /v2/images/generations + /v1/media img2img + polling /v1/media/{id})

## Этап 1 — сервисы и API
- [~] backend/app/services/: FunnelService (вопросы/условия/навигация), LeadService (заявки, идемпотентность), GenerationService (запрет без контакта, формирование описания+промпта, постановка job), BroadcastService (сегментация), ContentService (блоки/галерея/отзывы/FAQ), NotifyService (через MessengerAdapter)
- [~] backend/app/api/: публичный контент, отслеживание sources, приём заявок (fallback), health
- [ ] backend/app/admin/: dashboard, сайт, галерея, воронка, заявки (CSV), генерации, рассылки, отзывы, настройки — Jinja2+HTMX, авторизация, CSRF, rate limit, audit

## Этап 1 — мессенджер и workers
- [x] bot/adapters/: MessengerAdapter интерфейс, TelegramAdapter (aiogram 3.x), MaxAdapter (заглушка)
- [~] bot/: handlers (FSM воронка, deep links), keyboards, middlewares (DB session, source tracking), states
- [~] worker/generation_worker.py: polling jobs, вызов провайдера, сохранение, notify
- [~] worker/broadcast_worker.py: сегментация, rate limit, retry, исключение blocked, защита от дублей

## Этап 1 — frontend
- [x] frontend/: Vite, конфиг с base path GitHub Pages, VITE_* переменные
- [x] Секции: шапка, hero (владелец+кухня), генератор, галерея (фильтры+lightbox), варианты, о компании, этапы, материалы/фурнитура, отзывы, FAQ, контакты
- [~] Мобильная вёрстка 320-430px, планшет, десктоп; без горизонтального скролла
- [x] CTA → MAX-ссылка; временный Telegram fallback через deep links

## Этап 1 — CI/CD и развёртывание
- [x] .github/workflows/deploy-pages.yml (push main + workflow_dispatch, base path из имени репо, Pages)
- [x] deploy/systemd/: kitchen-api.service, kitchen-bot.service, kitchen-worker.service
- [x] deploy/nginx/kitchen.conf (/, /api, /admin, /media)
- [ ] Скрипты установки/бэкапа

## Этап 1 — тесты и проверка
- [ ] Тесты: создание сессии, переход по шагам, изменение ответа, сохранение фото, запрет генерации без контакта, получение контакта, создание заявки, формирование описания, формирование промпта, постановка job, повторная обработка update, рассылка, редактирование сайта, добавление отзыва, загрузка изображения, экспорт CSV
- [ ] Линтер (ruff), mypy
- [~] Проверка мобильной вёрстки
- [x] Обновление TASKS.md

## Этап 2 — перенос и MAX (после)
- [ ] Nginx для frontend + домен + HTTPS
- [ ] MaxAdapter (реальная реализация)
- [ ] Вебхук бота (опционально)
