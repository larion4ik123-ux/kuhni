"""backend.app — FastAPI-приложение платформы кухонь.

Слои (см. docs/ARCHITECTURE.md):
  core/          — settings, database, security, зависимости
  models/        — ORM-модели SQLAlchemy 2
  repositories/  — доступ к данным
  services/      — бизнес-логика (мессенджер-независимая)
  providers/     — ImageGenerationProvider и реализации
  api/           — публичный REST
  admin/         — Jinja2 + HTMX админпанель
  templates/, static/ — рендеринг и ассеты админки
"""
