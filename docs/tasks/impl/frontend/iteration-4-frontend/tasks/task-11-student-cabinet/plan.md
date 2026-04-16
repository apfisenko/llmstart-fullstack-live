# Задача 11: Кабинет студента (зона C)

## Цель

Заменить заглушку маршрута «Кабинет студента» полноценным экраном по зоне C: данные из `GET /api/v1/cohorts/{cohort_id}/memberships/{membership_id}/progress-overview`, сдача через `PUT .../progress-records/{checkpoint_id}` с полями `comment` и `submission_links` ([`docs/tech/api-contracts.md`](../../../../../../tech/api-contracts.md), [`docs/tech/frontend-requirements.md`](../../../../../../tech/frontend-requirements.md) §6.3).

## Источники

- [`docs/tasks/tasklist-frontend.md`](../../../../../../tasks/tasklist-frontend.md) — постановка задачи 11, DoD
- [`docs/ui/ui-requirements.md`](../../../../../../ui/ui-requirements.md) — экран 3 (продуктовые формулировки)
- [`docs/tech/frontend-requirements.md`](../../../../../../tech/frontend-requirements.md) — §6.3 зона C
- [`docs/api/openapi-v1.yaml`](../../../../../../api/openapi-v1.yaml) — схемы `progress-overview`, `PUT progress-records`

## Состав работ

1. **Route Handlers (Next BFF)** — по аналогии с `app/api/v1/cohorts/[cohort_id]/leaderboard/route.ts` и teacher-dashboard:
   - `GET` → проксирование на backend `.../memberships/{membership_id}/progress-overview` с тем же `Authorization` и базовым URL из env.
   - `PUT` → `.../progress-records/{checkpoint_id}` с телом JSON (`comment`, `submission_links` по OpenAPI).
2. **Типы** — `lib/student-progress-types.ts` (или расширение существующего модуля): чекпоинты, записи прогресса, сводка «следующий урок» из полей ответа API.
3. **Страница** — `app/(app)/student/page.tsx` (client или смесь RSC + client для формы): чтение `cohort_id`, `membership_id`, токена из [`WebSessionContext`](../../../../../../../frontend/web/components/web-session-context.tsx) / сессии входа; запрос overview; состояния loading / empty / error.
4. **Список уроков** — для каждого чекпоинта: статус `completed` + дата (зелёный акцент); первый доступный к сдаче — кнопка «Сдать задание»; остальные «будущие» без сдачи до текущего — disabled (логика по `sort_order` и статусам из ответа, согласованно с UI-доком).
5. **Форма сдачи** — shadcn `Dialog` или `Sheet`: текст отчёта; ссылки — отдельный ввод (одна строка / несколько полей / textarea с разбором строк — зафиксировать минимально передаваемый формат массива `submission_links` в API); submit → `PUT` → закрытие формы и refetch overview.
6. **Шапка** — приветствие по имени из сессии или из ответа overview, если API отдаёт display name; кнопка «Чат с ассистентом» → навигация на `/chat` (или документировать только FAB).
7. **Роль не student** — если после входа роль teacher: короткое сообщение и ссылка на дашборд преподавателя (без вызова student-only API с подставленным чужим `membership_id`).

## Критерии готовности

- Сквозной сценарий на mock-данных: войти как студент из сида → кабинет показывает уроки и счётчики → сдать текущий урок → после обновления урок отмечен сданным.
- Нет обхода backend и нет вызова LLM из браузера.
- `pnpm lint` и production build без ошибок.

## Риски и уточнения

- Если фактический JSON backend расходится с OpenAPI — при реализации обновить YAML и `api-contracts.md` в рамках этой же задачи (минимальный дифф).
- Поведение при 403 на `PUT` (например попытка сдать не тот чекпоинт) — показать сообщение пользователю без технических деталей.

## Документы по завершении

- Заполнить [summary.md](summary.md): факт реализации, отклонения от UI-дока, идентификаторы компонентов и маршрутов BFF.
