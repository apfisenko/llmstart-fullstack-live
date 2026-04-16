# Задача 05: Лидерборд (таблица / scatter)

## Цель

Страница лидерборда с переключателем «Таблица / Карта», данными из `GET /api/v1/cohorts/{cohort_id}/leaderboard`, визуализацией топ-3 и scatter по контракту итерации 4.

## Источники

- [docs/tasks/tasklist-frontend.md](../../../../../../tasks/tasklist-frontend.md) — постановка задачи 05
- [docs/tech/frontend-requirements.md](../../../../../../tech/frontend-requirements.md) — зона B
- [docs/ui/leaderboard.png](../../../../../../ui/leaderboard.png) — макет таблицы и переключателя
- [docs/api/openapi-v1.yaml](../../../../../../api/openapi-v1.yaml) — `LeaderboardResponse`

## Состав работ

1. Прокси Next: `app/api/v1/cohorts/[cohort_id]/leaderboard/route.ts`
2. Типы: `lib/leaderboard-types.ts`
3. UI: `components/leaderboard-table.tsx`, `components/leaderboard-scatter.tsx`
4. Страница: `app/(app)/leaderboard/page.tsx` — сессия, `viewer_membership_id`, loading/error/empty, переключатель без повторного запроса

## Критерии готовности

- Оба режима на данных mock; переключение без нового запроса
- Топ-3 визуально выделены; scatter с осями и подсказкой по точке
