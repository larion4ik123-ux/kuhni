# DEPLOYMENT

Два сценария. Подробности — ниже.

## Этап 1: GitHub Pages (сайт) + VPS (всё остальное)

```
GitHub Pages:  https://USERNAME.github.io/REPOSITORY/   ← frontend/dist
VPS (Ubuntu 24.04, 1 CPU/1ГБ/20ГБ):
  kitchen-api.service     Uvicorn  :8000   (API + админка)
  kitchen-bot.service     aiogram polling
  kitchen-worker.service  generation + broadcast workers
  SQLite:  backend/data/kitchen.db (WAL)
  Медиа:   backend/media/
Nginx (этап 2) / прямой порт (этап 1 для API)
```

### Frontend → GitHub Pages

1. В репозитории GitHub: **Settings → Pages → Source: GitHub Actions**.
2. Запушь в `main` — сработает `.github/workflows/deploy-pages.yml`.
3. Workflow собирает `frontend/` с `base` = `/<REPOSITORY>/` (учитывает имя репо)
   и публикует `dist` через `actions/upload-pages-artifact` + `actions/deploy-pages`.
4. `VITE_API_BASE_URL` и `VITE_TELEGRAM_BOT_URL` — в Secrets репозитория
   (переменные сборки). Не хранить секреты во frontend.
5. Сайт обращается к API на VPS; при недоступности API — fallback
   (статичный контент + сообщение «оставьте заявку в боте»).

### VPS — установка

```bash
# 1. Система
sudo apt update && sudo apt install -y python3.12 python3.12-venv nginx git
git clone <repo> /opt/kitchen && cd /opt/kitchen

# 2. Окружение
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .

# 3. Конфиг
cp .env.example .env
# Заполнить: SECRET_KEY, TELEGRAM_BOT_TOKEN, MANAGER_CHAT_IDS,
#            AI_API_KEY (polza.ai), VITE_* (если собираешь сайт здесь)

# 4. БД и медиа
alembic upgrade head
mkdir -p backend/data backend/media backups

# 5. Подготовить изображения (на машине с Pillow, затем скопировать assets/processed)
python scripts/process_images.py

# 6. systemd
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kitchen-api kitchen-bot kitchen-worker
```

### Проверка этапа 1

- `curl http://localhost:8000/api/health` → `{"status":"ok"}`
- Админка: `http://<vps-ip>:8000/admin/login` (или через Nginx при этапе 2).
- Бот: написать `/start` → воронка.
- Сайт: `https://USERNAME.github.io/REPOSITORY/` → кнопки ведут в бота.

## Этап 2: всё на VPS + Nginx + домен + MAX

1. **Домен:** A-запись → IP VPS. HTTPS — certbot/Let's Encrypt.
2. **Frontend** собирается на VPS (или CI) с `VITE_API_BASE_URL=https://<домен>`
   и `VITE_TELEGRAM_BOT_URL` (или `MAX_BOT_URL`). `dist` кладётся в
   `/var/www/kitchen`.
3. **Nginx** (см. `deploy/nginx/kitchen.conf`):
   - `/` → `/var/www/kitchen` (статика)
   - `/api` → `proxy_pass http://127.0.0.1:8000`
   - `/admin` → `proxy_pass http://127.0.0.1:8000`
   - `/media` → `alias /opt/kitchen/backend/media`
4. **Бот:** при этапе 2 можно переключиться на webhook (Nginx → `/api/bot/webhook`)
   или оставить polling. Смена — настройкой.
5. **MAX:** реализовать `MaxAdapter` (`bot/adapters/max_adapter.py`) по
   интерфейсу `MessengerAdapter`. В `.env` выставить `MESSENGER=max`
   (или оставить оба). Воронка/заявки/генерация не меняются.

### Nginx-схема маршрутов

```
/                 → статика frontend/dist
/api/*            → Uvicorn (FastAPI)
/admin/*          → Uvicorn (FastAPI admin)
/media/*          → файлы с диска (alias)
/static/*         → статика админки (FastAPI StaticFiles)
```

## Перенос с GitHub Pages на VPS без переделки

Достаточно:
1. Собрать `frontend` с новыми `VITE_*` переменными.
2. Разместить `dist` в `/var/www/kitchen`.
3. Настроить Nginx.

Компоненты frontend не переписываются — `base path` и API URL берутся из
переменных сборки.

## Оптимизация под 1 ГБ RAM

- Один Uvicorn worker (`--workers 1`).
- Worker — отдельный процесс, polling `jobs`.
- SQLite WAL, `synchronous=NORMAL`.
- Оригиналы изображений не хранятся в полном размере без лимита
  (`MAX_UPLOAD_MB`, `fullscreen` ≤ 1920px).
- Временные файлы генерации удаляются по `GENERATION_RETENTION_DAYS`.
- Логи ротируются (`logrotate` / systemd журналирование).
- ML-модели локально не загружаются — генерация в polza.ai.

## Резервное копирование SQLite

```bash
# cron, ежедневно
sqlite3 backend/data/kitchen.db ".backup '$BACKUP_DIR/kitchen-$(date +%F).db'"
find $BACKUP_DIR -mtime +$BACKUP_RETENTION_DAYS -delete
```
WAL-режим позволяет бэкапить «на горячую».
