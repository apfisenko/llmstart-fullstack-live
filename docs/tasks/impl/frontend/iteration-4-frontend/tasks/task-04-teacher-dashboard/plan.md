# Задача 04: панель преподавателя

## Цель

Страница `/teacher`: KPI, график активности по дням, таблица Q&A с пагинацией и поиском, лента сдач с деталями, матрица прогресса; данные из `GET /api/v1/cohorts/{cohort_id}/teacher-dashboard` через Next Route Handler (Bearer на сервере).

## Решения

| Тема | Выбор |
|------|--------|
| Вызов API | Клиент → `GET /api/v1/cohorts/:id/teacher-dashboard` на origin Next; Route Handler проксирует на `BACKEND_ORIGIN` с `Authorization` при наличии токена |
| Сессия | `viewer_membership_id` = `membership_id` из `WebSession` при `role === teacher` |
| Не-преподаватель | Запрос не выполняется; сообщение + ссылка на `/student` |
| График | Линия по `activity_by_day` на чистом SVG (без recharts), `activity_days=14` по умолчанию |
| Пагинация Q&A | `turns_cursor` + накопление `items` на клиенте; при смене `q` — сброс |

## Ссылки

- [tasklist](../../../../../tasklist-frontend.md) задача 04
- [api-contracts](../../../../../../tech/api-contracts.md)
- [frontend-requirements](../../../../../../tech/frontend-requirements.md)
- [openapi](../../../../../../api/openapi-v1.yaml) `TeacherDashboardResponse`
