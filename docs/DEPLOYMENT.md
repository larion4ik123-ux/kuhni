# Deployment

Проект публикуется в двух местах:

- основной сайт: `https://194-147-78-106.sslip.io/`;
- резервная демонстрация: `https://larion4ik123-ux.github.io/kuhni/`.

MAX-бот работает на основном VPS через HTTPS webhook. GitHub Pages содержит
только статическую копию сайта и не принимает webhook.

## Сборка frontend

```bash
npm ci --prefix frontend
npm run build --prefix frontend
```

Скрипт `prebuild` переносит оптимизированные изображения в
`frontend/public/media`. Содержимое `frontend/dist` копируется:

- в `/var/www/interier/` на VPS;
- в ветку `gh-pages` для резервной демонстрации.

На VPS каталог `frontend/dist/media/` также копируется без удаления файлов в
`/opt/kitchen-platform/backend/media/`. Nginx отдаёт из него и изображения
сайта, и сохранённые результаты генерации.

## Установка backend на VPS

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv nginx

cd /opt/kitchen-platform
python3.12 -m venv .venv
.venv/bin/pip install -e .

mkdir -p backend/data backend/media backups
sudo chown -R www-data:www-data backend/data backend/media backups

sudo -u www-data .venv/bin/alembic upgrade head
sudo -u www-data .venv/bin/python -m backend.app.seed

sudo cp deploy/systemd/kitchen-api.service /etc/systemd/system/
sudo cp deploy/systemd/kitchen-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kitchen-api kitchen-worker
```

Файл `.env` хранится с правами `root:www-data 640`. До подключения бота поля
`MAX_BOT_TOKEN`, `MAX_BOT_URL`, `MAX_MANAGER_CHAT_IDS` и `AI_API_KEY` остаются
пустыми. Пустые значения не заменяются тестовыми ключами.

## Подключение MAX

После получения токена и прямой ссылки на бота заполнить:

```dotenv
MAX_BOT_TOKEN=...
MAX_BOT_URL=https://max.ru/...
MAX_WEBHOOK_URL=https://194-147-78-106.sslip.io/api/max/webhook
MAX_WEBHOOK_SECRET=...
MAX_MANAGER_CHAT_IDS=123456789
AI_PROVIDER=openai_compatible
AI_API_BASE_URL=https://polza.ai/api/v1
AI_API_KEY=...
AI_MODEL=bytedance/seedream-4.5
```

Затем зарегистрировать webhook и перезапустить сервисы:

```bash
sudo -u www-data .venv/bin/python -m bot.main --register-webhook
sudo systemctl restart kitchen-api kitchen-worker
```

Frontend пересобирается с `VITE_MAX_BOT_URL`, после чего видимые MAX-кнопки
становятся активными ссылками.

## Nginx

Конфигурация `deploy/nginx/interier-sslip.conf` обслуживает:

```text
/                 -> /var/www/interier
/api/*            -> FastAPI на 127.0.0.1:8000
/media/*          -> /opt/kitchen-platform/backend/media
```

Перед применением:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Проверка

```bash
curl https://194-147-78-106.sslip.io/api/health
systemctl is-active kitchen-api kitchen-worker
```

До выдачи реальных секретов health должен вернуть `max_configured: false` и
`ai_configured: false`. Это штатное безопасное состояние, а не ошибка.
