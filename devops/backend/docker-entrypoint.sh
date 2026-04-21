#!/bin/sh
set -e
# В контейнере хост БД — сервис postgres, не 127.0.0.1 из локального backend/.env.
# Compose задаёт DOCKER_DATABASE_URL; экспорт гарантирует и Alembic, и uvicorn.
if [ -n "$DOCKER_DATABASE_URL" ]; then
  export DATABASE_URL="$DOCKER_DATABASE_URL"
  echo "[entrypoint] DATABASE_URL указывает на сервис postgres (Docker)." >&2
fi
cd /app
/app/.venv/bin/alembic upgrade head
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
