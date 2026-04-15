# Задача 02: реализация API и сидов для frontend (backend)

## Цель

Реализовать в ядре все HTTP-эндпоинты и данные, зафиксированные в задаче 01 и в [`docs/api/openapi-v1.yaml`](../../../../../api/openapi-v1.yaml) / [`docs/tech/api-contracts.md`](../../../../../tech/api-contracts.md); наполнить БД **mock-данными**, достаточными для экранов 04–07; завести учётную запись преподавателя **@akozhin** (`telegram_user_id` **162684825** по tasklist).

## Входные артефакты

| Документ | Назначение |
|----------|------------|
| [План задачи 01](../task-01-ui-api-contracts/plan.md) | Передача: миграции, эндпоинты, права, сиды |
| [`docs/data-model.md`](../../../../../data-model.md) | Целевая схема; расхождения с ORM — §«Соответствие реализации» |
| [`docs/tech/frontend-requirements.md`](../../../../../tech/frontend-requirements.md) | Сводка сценариев веба |

## Текущее состояние backend (отправная точка)

- Роутер v1: [`backend/app/api/v1/router.py`](../../../../../../backend/app/api/v1/router.py) — подключены `routes_dialogues`, `routes_guest`, `routes_cohort`.
- Уже есть: `GET/PUT` progress, `GET .../summary`, диалоги (сообщения, reset), guest assistant.
- Сервис потока: [`backend/app/services/cohort_service.py`](../../../../../../backend/app/services/cohort_service.py) + [`CohortProgressRepository`](../../../../../../backend/app/infrastructure/repositories/cohort_progress_repository.py).
- ORM: [`backend/app/domain/models.py`](../../../../../../backend/app/domain/models.py) — у `User` есть `telegram_user_id` (строка), **`telegram_username` нет**; у `ProgressCheckpoint` **нет `is_homework`**; у `ProgressRecord` **нет `submission_links`**.

## 1. Схема БД и ORM (Alembic)

Одна или несколько ревизий Alembic (`backend/migrations/versions/`), без ломания существующих FK:

| Изменение | Таблица | Комментарий |
|-----------|---------|--------------|
| Колонка `telegram_username` | `users` | `text`, nullable, **частичный уникальный индекс** на ненулевые значения (см. [`postgresql-table-design`](../../../../../../.cursor/skills/postgresql-table-design/SKILL.md)); нормализация в сервисе (trim, без `@`, регистр — одно правило на весь проект). |
| Колонка `is_homework` | `progress_checkpoints` | `boolean`, NOT NULL, default `false`. |
| Колонка `submission_links` | `progress_records` | `jsonb` nullable, массив строк URL (или `text[]` — выбрать один вариант и зафиксировать в ADR/summary при отличии от data-model). |

После миграции: обновить **ORM-модели**, репозитории и Pydantic-схемы ответов так, чтобы **`is_homework`** попадало во все ответы с `ProgressCheckpointItem` (в т.ч. `list_progress_checkpoints`, `summary`, новые агрегаты).

**Выравнивание с документацией:** при изменении физической схемы — синхронно править [`docs/data-model.md`](../../../../../data-model.md), если факт отличается от текста (имена колонок FK в ORM и т.д.).

## 2. Новые эндпоинты (контракт задачи 01)

Реализовать в FastAPI с теми же зависимостями, что у существующих маршрутов: `require_client_token_if_configured`, инъекция сессии БД, единый [`ApiError`](../../../../../../backend/app/api/errors.py).

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/api/v1/auth/dev-session` | По `telegram_username` найти `User`, вернуть `user_id`, `display_name` (из `name`), `memberships[]`, опционально `web_dialogue_id` активного диалога канала `web`. **404** если пользователь не найден. |
| `GET` | `/api/v1/cohorts/{cohort_id}/teacher-dashboard` | Агрегат панели преподавателя: KPI с недельной дельтой, `activity_by_day`, `recent_turns` (пагинация `turns_cursor`, `limit`, `q`), `recent_submissions`, `matrix`. Query **`viewer_membership_id`** обязателен, роль — **teacher**, `cohort_id` совпадает. |
| `GET` | `/api/v1/cohorts/{cohort_id}/leaderboard` | Рейтинг + поля для таблицы и scatter. Query **`viewer_membership_id`** — опционально (политика: публичный экран vs только участники потока — **зафиксировать в коде и summary**). |
| `GET` | `/api/v1/cohorts/{cohort_id}/memberships/{membership_id}/progress-overview` | Чекпоинты потока + записи прогресса для **этого** участия; проверка `membership` ∈ `cohort`, вызывающий контекст MVP (Bearer + тот же membership или общий токен + явный id — согласовать с текущими правилами `put_progress_record`). |
| `GET` | `/api/v1/dialogues/{dialogue_id}/turns` | Список `DialogueTurn` по `dialogue_id` с сортировкой по `asked_at` DESC, пагинация `before_asked_at` + `limit`; проверка принадлежности диалога к membership/cohort и права чтения. |

**Расширение существующих:**

- `PUT .../progress-records/{checkpoint_id}` — принять и сохранить **`submission_links`**; вернуть в `ProgressRecordResponse`.
- `GET .../progress-checkpoints` — включить **`is_homework`** в каждый элемент.

**Регистрация роутов:** новый модуль, например `routes_auth.py` для `dev-session`; расширить `routes_cohort.py` или вынести `routes_teacher.py` / методы в сервисе — на усмотрение исполнителя, без раздувания одного файла сверх разумного.

## 3. Запросы и производительность (минимум для MVP)

- **Teacher-dashboard:** SQL/запросы через репозиторий или SQLAlchemy: KPI за текущую и предыдущую календарную неделю; ряд по дням за `activity_days`; лента ходов — join `dialogue_turns` → `dialogues` → `cohort_memberships` при фильтре `cohort_id`; матрица — по сути расширение логики `summary` + `updated_at` по ячейкам. Избегать N+1 на MVP-объёме; при необходимости один запрос с подзапросами или 2–3 чётких запроса.
- **Leaderboard:** отсортированный список студентов, счётчики уроков/ДЗ, `per_checkpoint`, поля `scatter_x` / `scatter_y` по правилам из [плана задачи 01](../task-01-ui-api-contracts/plan.md) §зона B.
- **Диалог turns:** индекс `(dialogue_id, asked_at)` уже в модели — использовать в `WHERE` пагинации.

Детали полей — **строго по OpenAPI**; при расхождении YAML ↔ желаемая логика — править YAML и `api-contracts.md` в рамках этой же задачи.

## 4. Сиды и преподаватель @akozhin

- После миграций: **одна демо-когорта** с несколькими студентами, чекпоинтами (часть с `is_homework: true`), прогрессом, ходами диалога (telegram и/или web), достаточными для KPI и графика.
- Пользователь преподавателя: **`telegram_user_id = 162684825`**, **`telegram_username`** нормализованный для **akozhin** (без `@`), `name` по желанию; **membership** с ролью `teacher` в той же когорте.
- Студенты: разные `telegram_username` для проверки входа и лидерборда.

Способ: data-migration Alembic **или** отдельная команда/скрипт + цель в [Makefile](../../../../../../Makefile) (как в критериях блока 1 tasklist). Выбор — зафиксировать в `summary.md`.

## 5. Тесты

- **pytest + httpx** `AsyncClient` + `ASGITransport` для каждого нового маршрута: успех, 401 при отключённом/неверном токене (если настроено), 403/404 на граничных случаях.
- Минимум: `dev-session`, один сценарий `teacher-dashboard`, `leaderboard`, `progress-overview`, `dialogue turns`, `put_progress_record` с `submission_links`.

## 6. Документация и синхронизация

- После реализации: **`GET /openapi.json`** — сверить с [`docs/api/openapi-v1.yaml`](../../../../../api/openapi-v1.yaml); обновить YAML при расхождениях.
- [`docs/tech/api-contracts.md`](../../../../../tech/api-contracts.md) — убрать пометки «реализация — задача 02» там, где поведение стало фактом; при изменении контракта — актуализировать таблицу эндпоинтов.

## 7. Makefile и README

- Добавить/уточнить цели для сида демо-данных (если отдельный шаг) и кратко описать в [README](../../../../../../README.md) под PowerShell (см. tasklist «Завершение блока 1»).

## Порядок выполнения (рекомендуемый)

1. Миграции + ORM + расширение `PUT`/`GET` checkpoints.  
2. `POST /auth/dev-session`.  
3. `GET .../progress-overview`.  
4. `GET .../dialogues/.../turns`.  
5. `GET .../leaderboard`.  
6. `GET .../teacher-dashboard` (самый объёмный).  
7. Сиды + Makefile/README.  
8. Тесты + синхронизация OpenAPI/контрактов.

## Критерии готовности (сверка с tasklist)

- Новые пути соответствуют контракту задачи 01; тесты на критичные ветки зелёные.  
- `make db-migrate` (или принятый в репо способ) на чистой БД + сид даёт когорту, mock-данные и пользователя с `telegram_user_id = 162684825`.  
- `/docs` или OpenAPI показывают новые операции.

## Skills

[`api-design-principles`](../../../../../../.cursor/skills/api-design-principles/SKILL.md), [`postgresql-table-design`](../../../../../../.cursor/skills/postgresql-table-design/SKILL.md), [`python-testing-patterns`](../../../../../../.cursor/skills/python-testing-patterns/SKILL.md), [`fastapi-templates`](../../../../../../.cursor/skills/fastapi-templates/SKILL.md) при добавлении роутеров/зависимостей.

## Документы задачи

- План: этот файл.  
- Итог: [summary.md](summary.md) (заполнить по завершении).
