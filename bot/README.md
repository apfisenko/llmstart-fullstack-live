# LLMStart — Telegram-бот

Тонкий клиент backend: сообщения и команды уходят в HTTP API ядра (`/api/v1/`), без собственной бизнес-логики потока.

## Быстрый старт

1. Скопируйте [`bot/.env.example`](.env.example) → **`bot/.env`**.
2. Задайте **`TELEGRAM_TOKEN`**, **`BACKEND_BASE_URL`** (например `http://127.0.0.1:8000`).
3. Поднимите backend и при необходимости Postgres (см. корневой [README.md](../README.md) или [docs/onboarding.md](../docs/onboarding.md)).
4. Из **корня** репозитория:

   ```bash
   make install
   make run
   ```

   Windows (PowerShell):

   ```powershell
   .\tasks.ps1 install
   .\tasks.ps1 bot-dev
   ```

Остальные переменные (`COHORT_ID`, `MEMBERSHIP_ID`, guest-режим, Bearer, прокси) — в [README.md](../README.md) (раздел «Telegram-бот») и в комментариях [`bot/.env.example`](.env.example).

## Документация

- [Онбординг](../docs/onboarding.md)
- [Архитектура](../docs/architecture.md)
- [Интеграции и секреты](../docs/integrations.md)
