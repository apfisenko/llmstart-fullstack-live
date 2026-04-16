# Задача 03: каркас Next.js + бот (итерация 4)

## Цель

Единый веб-проект в `frontend/web/` (App Router, pnpm, shadcn/ui, тёмная тема), вход по `POST /api/v1/auth/dev-session`, layout с навигацией и каркасом глобального чата; команды Makefile и `tasks.ps1`; минимальное расширение бота для ввода username.

## Решения

| Тема | Выбор |
|------|--------|
| Маршруты приложения | `/login`, `/teacher`, `/leaderboard`, `/student`, `/chat`; корень `/` редиректит по наличию сессии в `localStorage` |
| Сессия веба | Ключ `llmstart_web_session_v1`, объект `WebSession` (плоские поля выбранного участия); первое участие с ролью `teacher`, иначе первое в списке |
| Прокси к API | `app/api/v1/auth/dev-session/route.ts` — `BACKEND_ORIGIN` обязателен; `Authorization: Bearer` добавляется только если задан `BACKEND_API_CLIENT_TOKEN` (как на backend) |
| Защита маршрутов | Клиентский `AppShell`: после `setTimeout(0)` читает `localStorage`, без сессии → `/login` |
| Чат в задаче 03 | FAB + Sheet, заглушка текста |
| Бот | `/username <arg>` и `/login` + следующее сообщение → `lookup_dev_session`; состояние ожидания в `bot/state/pending_dev_username.py` (память процесса) |

## Ссылки

- [tasklist](../../../../../tasklist-frontend.md) задача 03
- [api-contracts](../../../../../../tech/api-contracts.md)
- [frontend-requirements](../../../../../../tech/frontend-requirements.md)
