# Задача 11: Кабинет студента — summary

## Статус

Завершена: экран зоны C, BFF-маршруты, форма сдачи через `PUT .../progress-records/{checkpoint_id}`.

## Факт реализации

- **BFF:** `GET` [frontend/web/app/api/v1/cohorts/[cohort_id]/memberships/[membership_id]/progress-overview/route.ts](../../../../../../../frontend/web/app/api/v1/cohorts/[cohort_id]/memberships/[membership_id]/progress-overview/route.ts), `PUT` [frontend/web/app/api/v1/cohorts/[cohort_id]/memberships/[membership_id]/progress-records/[checkpoint_id]/route.ts](../../../../../../../frontend/web/app/api/v1/cohorts/[cohort_id]/memberships/[membership_id]/progress-records/[checkpoint_id]/route.ts) — прокси на backend по образцу лидерборда.
- **Типы:** [frontend/web/lib/student-progress-types.ts](../../../../../../../frontend/web/lib/student-progress-types.ts) (ответ overview, `PutProgressRecordRequest`, `ProgressRecordResponse`; чекпоинты через `LeaderboardCheckpointItem`).
- **UI:** [frontend/web/app/(app)/student/page.tsx](../../../../../../../frontend/web/app/(app)/student/page.tsx) — сессия из `readWebSession()`, ветка для `role === "teacher"` без вызова overview, объединение `checkpoints` + `records`, первый доступный к сдаче этап (предыдущие по `sort_order` должны быть `completed` или `skipped`), Sheet справа для отчёта и ссылок (по строке, до 32 URL), после успеха — refetch overview.
- **Проверки:** `pnpm lint`, `pnpm build` — успешно.

## Ручная проверка (студент из сида)

После миграции `0007_seed_frontend_demo_cohort` войти с **Telegram username** одного из демо-студентов (только студенческое участие, без конфликта с `pickMembership`): **`demo_student_alpha`**, **`demo_student_beta`** или **`demo_student_gamma`** (`backend/migrations/versions/0007_seed_frontend_demo_cohort.py`). Пользователь **akozhin** в сессии получает роль преподавателя — на `/student` показывается подсказка со ссылкой на `/teacher`.

## Отклонения от UI-дока

- Вместо отдельного компонента Dialog из shadcn использован уже подключённый **Sheet** (как на панели преподавателя для просмотра сдачи).
- Ссылки вводятся одним textarea «по строке», без отдельных полей на каждую ссылку.

## Не вошло в задачу

- Изменение логина (`pickMembership` / выбор роли при нескольких membership) не делалось; для кабинета студента нужен вход под учёткой со студенческим участием (см. выше).
