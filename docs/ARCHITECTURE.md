# ARCHITECTURE

## Принципы

1. **Бизнес-логика мессенджер-независима.** Воронка, заявки, генерация, рассылки
   живут в `backend/app/services` и не знают про Telegram/MAX.
2. **Мессенджер — адаптер.** `MessengerAdapter` (`bot/adapters/`) — единственная
   точка, знающая specifics конкретного мессенджера.
3. **AI-провайдер — абстракция.** `ImageGenerationProvider`
   (`backend/app/providers/`) — интерфейс; реализация выбирается в настройках.
4. **Контент редактируется, не зашивается в код.** Тексты сайта, воронка,
   отзывы, материалы — в БД, управляются через админпанель.
5. **Лёгкий стек.** 1 ГБ RAM: один Uvicorn worker, отдельный Python worker,
   SQLite WAL, без Redis/Kubernetes/Node.js в production.

## Слои

```
┌─────────────────────────────────────────────────────────┐
│  frontend (Vite → статический dist)                      │  GitHub Pages / Nginx
│  Публичный сайт. CTA → MAX-ссылка; на этапе 1 fallback   │
│  может вести в Telegram-бот (deep links).                │
└───────────────┬─────────────────────────────────────────┘
                │ HTTPS (VITE_API_BASE_URL)
┌───────────────▼─────────────────────────────────────────┐
│  backend/app/api      — публичный REST (контент, заявки) │
│  backend/app/admin    — Jinja2 + HTMX админпанель         │
├─────────────────────────────────────────────────────────┤
│  backend/app/services  — бизнес-логика (мессенджер-       │
│                          независимая): воронка, заявки,  │
│                          генерация, рассылки, контент     │
├─────────────────────────────────────────────────────────┤
│  backend/app/providers — ImageGenerationProvider          │
│  backend/app/repositories — доступ к данным (SQLAlchemy)  │
│  backend/app/models    — ORM-модели                        │
│  shared/               — enum, константы, общие схемы     │
└───────────────┬─────────────────────────────────────────┘
                │ таблица jobs (polling)
┌───────────────▼─────────────────────────────────────────┐
│  worker/  generation_worker.py  — AI-генерация            │
│           broadcast_worker.py   — рассылки                │
└───────────────┬─────────────────────────────────────────┘
                │ MessengerAdapter
┌───────────────▼─────────────────────────────────────────┐
│  bot/adapters/TelegramAdapter (aiogram 3.x)              │  этап 1
│  bot/adapters/MaxAdapter       (заглушка, этап 2)         │  этап 2
└─────────────────────────────────────────────────────────┘
```

## Поток заявки

```
Сайт (CTA MAX/fallback) ──deep link start=website_generator──▶ TelegramAdapter / MaxAdapter
   │
   ▼
Воронка (FSM, вопросы из БД) ──ответы + фото──▶ funnel_answers
   │
   ▼
services.GenerationService.create_job() ──▶ jobs (status=pending)
   ▼
generation_worker.poll() ──▶ ImageGenerationProvider.generate()
   │   (polza.ai /v1/media img2img с фото помещения)
   ▼
generated_images + jobs(done) ──▶ предварительная визуализация пользователю
   │
   ▼
Пользователь нажимает «Передать заявку Артёму» ──▶ contact + lead + NotifyService
   │
   ▼
Артём связывается с клиентом, уточняет замер и следующий шаг
```

**Целевой инвариант:** контакт не должен быть условием генерации. Визуализация
даёт пользователю понятную идею, а контакт запрашивается отдельно для передачи
заявки Артёму. Бот не рассчитывает и не обещает точную стоимость.

## Разделение для этапа 2

| Что меняется | Что НЕ меняется |
|---|---|
| `MaxAdapter` реализует `MessengerAdapter` | `services/`, `models/`, воронка, генерация |
| frontend переезжает на Nginx | сборка dist, компоненты |
| `MAX_*` env вместо `TELEGRAM_*` | `settings`, провайдеры, API |
| домен в `VITE_API_BASE_URL` | структура API |

## Процесс-модель (1 ГБ RAM)

- `kitchen-api.service` — Uvicorn, 1 worker, API + админка (FastAPI).
- `kitchen-bot.service` — aiogram polling (или webhook на этапе 2).
- `kitchen-worker.service` — polling таблицы `jobs`, обработка генераций и рассылок.

БД — SQLite WAL. Файлы — на диске (`MEDIA_DIR`), в БД только пути.
ML-модели локально не загружаются — генерация во внешнем API (polza.ai).
