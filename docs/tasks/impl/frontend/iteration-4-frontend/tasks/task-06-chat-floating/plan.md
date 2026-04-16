# Задача 06: Глобальный чат (плавающая панель)

## Цель

Плавающая панель чата на всех экранах `(app)`: история и отправка через backend API, стиль «терминал / IDE», без streaming (полный JSON-ответ).

## Источники

- [docs/tasks/tasklist-frontend.md](../../../../../../tasks/tasklist-frontend.md) — постановка задачи 06
- [docs/tech/frontend-requirements.md](../../../../../../tech/frontend-requirements.md) — зона D
- [docs/tech/api-contracts.md](../../../../../../tech/api-contracts.md) — таблица «Чат (D)»
- [docs/ui/ui-requirements.md](../../../../../../ui/ui-requirements.md) — глобальный чат

## Согласование с задачей 07

Один активный диалог веб-клиента: идентификатор хранится в **`WebSession.web_dialogue_id`** (localStorage), обновляется из ответа `POST .../dialogues/messages`. Страница «Чат» в задаче 07 использует тот же `web_dialogue_id`.

## Состав работ

1. Прокси Next (Bearer на сервере): `app/api/v1/cohorts/[cohort_id]/dialogues/messages/route.ts` (POST), `app/api/v1/dialogues/[dialogue_id]/turns/route.ts` (GET), `app/api/v1/dialogues/[dialogue_id]/reset/route.ts` (POST).
2. Типы и разбор ошибок: `lib/dialogue-api.ts`.
3. Сессия: `lib/session.ts` — `patchWebSession` для обновления `web_dialogue_id`.
4. UI: `components/chat-widget-shell.tsx` — FAB, Sheet, загрузка истории, отправка, сброс, состояния ошибок; пропсы `session`, `onSessionChange` из `components/app-shell.tsx`.

## Критерии готовности

- С любой страницы приложения: открыть панель, отправить сообщение, увидеть ответ; F5 — история подгружается при наличии `web_dialogue_id`.
- Закрытие панели не меняет маршрут.
- `pnpm lint` в `frontend/web/`.
