# DATABASE

СУБД: SQLite (WAL mode) на этапе 1, готовность к PostgreSQL.
ORM: SQLAlchemy 2 (async), миграции: Alembic. Файлы — на диске, в БД только пути.

## WAL и индексы

При инициализации подключения выполняется `PRAGMA journal_mode=WAL;` и
`PRAGMA synchronous=NORMAL;`. Индексы создаются на внешних ключах и полях
фильтрации (статусы, даты, source). Полнотекстовый поиск — `LIKE` (SQLite) /
`ILIKE` (PostgreSQL); Elasticsearch не используется.

## Модели

### admins
Администраторы админпанели. `id, username, password_hash, is_active, created_at`.
Пароли — bcrypt (passlib).

### users
Пользователи бота/сайта (без аутентификации, идентификация по мессенджер-аккаунту).
`id, created_at, updated_at`.

### messenger_accounts
Привязка пользователя к мессенджеру. `id, user_id, messenger ('telegram'|'max'),
account_id (chat_id / max id), username, first_name, last_name, created_at`.
UNIQUE(messenger, account_id).

### user_contacts
Контакты, переданные пользователем. `id, user_id, phone, first_name, last_name,
source, created_at`. Один пользователь может иметь несколько (история), но
«активный» берётся последний.

### funnel_questions
Настраиваемые вопросы воронки. `id, key (уникальный), title, description, type
(enum QuestionType), media_file_id, order, required, active, allow_skip,
generation_key, condition (JSON: когда показывать), next_question_rule (JSON:
какой следующий), created_at, updated_at`.

Типы (`QuestionType`): `single_choice, multiple_choice, text, number, range,
photo, contact, confirmation`.

### funnel_options
Варианты ответов на вопросы. `id, question_id, title, description, media_file_id,
internal_code, generation_hint, active, order`. `generation_hint` — текст для
AI-промпта (не только название).

### funnel_sessions
Сессии прохождения воронки. `id, user_id, messenger_account_id, status
('in_progress'|'completed'|'abandoned'), source (deep link: website_generator,
website_gallery, organic), current_question_id, created_at, updated_at,
completed_at`.

### funnel_answers
Ответы в сессии. `id, session_id, question_id, option_ids (JSON array),
value_text, value_number, media_file_id (для photo), created_at, updated_at`.

### leads
Заявки. `id, user_id, session_id, phone, status (LeadStatus), source,
selection_description (сформированный текст), generation_job_id, manager_comment,
created_at, updated_at`. Статусы: `new, contacted, measurement_scheduled,
quote_sent, in_progress, completed, rejected`.

### lead_status_history
История смены статусов. `id, lead_id, old_status, new_status, changed_by
(admin id | null=system), comment, created_at`.

### site_blocks
Редактируемые блоки сайта. `id, key (уникальный: hero_title, hero_subtitle,
about_text, ...), title, content (text/JSON), media_file_id, order, visible,
created_at, updated_at`. Группировка по секциям через `key` префикс.

### gallery_items
Работы в галерее. `id, media_file_id, caption, layout (прямая/угловая/п-образная/
остров), style (современный/неоклассика/классика), primary_color, alt_text,
focus_point (JSON {x,y}), display_order, is_real_work (bool), visible,
created_at`.

### reviews
Отзывы. `id, author_name, text, rating (1-5), review_date, source
('yandex'|'manual'|'widget'), source_url, display_order, visible, created_at`.
Без выдуманных — только реальные со ссылкой; если `source_url` пуст → блок скрыт.

### media_files
Метаданные файлов на диске. `id, category (kitchens/owner/facades/colors/
handles/countertops/logo/review/generated/upload), original_filename, stored_path,
webp_path, jpg_path, mime, width, height, size_bytes, sha256, is_real_work,
created_at, expires_at (для временных файлов генерации)`.

### generation_jobs
Задачи генерации (очередь). `id, lead_id, user_id, session_id, status
('pending'|'running'|'done'|'failed'|'cancelled'), provider, model, prompt
(итоговый), params (JSON), result_media_file_id, error, cost, attempt,
created_at, started_at, finished_at`.

### generated_images
Результаты генерации (1 job → N изображений). `id, job_id, media_file_id,
variant_index, created_at`.

### broadcasts
Рассылки. `id, title, text, media_file_id, buttons (JSON), segment
('all'|'with_contact'|'incomplete_funnel'|'got_result'), status
('draft'|'scheduled'|'running'|'done'|'stopped'|'failed'), total, sent, failed,
created_at, started_at, finished_at`.

### broadcast_recipients
Получатели рассылки. `id, broadcast_id, user_id, status
('pending'|'sent'|'failed'|'blocked'), error, sent_at`.

### settings
Ключ-значение настройки (редактируемые из админпанели). `id, key (unique),
value (text), category, updated_at`. Покрывает: telegram_bot_url, manager_chat_ids,
ai_api_url, ai_api_key (зашифрован/в env), ai_model, max_url (будущее),
yandex_maps_url, yandex_widget_html, retention_days, consent_texts, и т.д.

### jobs
Универсальная очередь фоновых задач (без Redis). `id, type ('generation'|
'broadcast'|'cleanup'), payload (JSON), status ('pending'|'running'|'done'|
'failed'), attempts, max_attempts, run_after, locked_at, error, created_at,
updated_at`. Worker polling с `SELECT ... FOR UPDATE SKIP LOCKED` (PostgreSQL) /
транзакционная блокировка (SQLite).

### audit_logs
Журнал действий админа. `id, admin_id, action, target_type, target_id, details
(JSON), ip, created_at`.

## Связи и ограничения

- Удаление пользователя каскадно → messenger_accounts, user_contacts,
  funnel_sessions, leads. Воронка и контент — soft (visible/active).
- `generation_jobs.lead_id` — один к одному (одна заявка → одна генерация;
  «другой вариант» создаёт новый lead/job).
- Идемпотентность: повторная обработка Telegram update не создаёт дубль
  lead — проверка по `(session_id)` или `(user_id, source, created_today)`.

## Миграции

Alembic: `backend/migrations/`. Начальная миграция создаёт все таблицы;
seed-скрипт (`backend/app/seed.py`) заполняет: вопросы воронки, варианты
(планировки/стили/цвета/ручки/фасады/фурнитура), блоки сайта, материалы,
FAQ, этапы работы. Seed идемпотентен (upsert по key).
