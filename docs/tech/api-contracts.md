# HTTP API v1: контракт (backend)

Сводка публичного API ядра для клиентов (Telegram-бот, веб). Согласовано с [`data-model.md`](../data-model.md), [`vision.md`](../vision.md), ADR-002 (FastAPI + OpenAPI).

## Источник правды по схемам

| Этап | Где смотреть |
|------|----------------|
| Черновик до/параллельно коду | [`docs/api/openapi-v1.yaml`](../api/openapi-v1.yaml) |
| После scaffold backend | `GET /openapi.json` на хосте приложения; при включении — UI `/docs` (**приоритет** над YAML при расхождении) |

## Версионирование и базовый URL

- Префикс: **`/api/v1/`**. Ломающие изменения — только в **`/api/v2/`** (или новом мажорном префиксе).
- Базовый URL задаётся средой (например `http://127.0.0.1:8000` локально; в проде — HTTPS).

Служебные маршруты вне контракта v1: `GET /health` (процесс), `GET /health/db` (проверка подключения к настроенной БД через `SELECT 1`); документация OpenAPI — см. задачу scaffold backend.

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/api/v1/auth/dev-session` | MVP-вход веба: по `telegram_username` вернуть `user_id`, участия в потоках, опционально `web_dialogue_id` |
| `POST` | `/api/v1/cohorts/{cohort_id}/dialogues/messages` | Сообщение в диалог: создать/продолжить `Dialogue`, сохранить ход (`DialogueTurn`), вызвать LLM, вернуть ответ ассистента |
| `GET` | `/api/v1/dialogues/{dialogue_id}/turns` | История диалога: список ходов (вопрос + ответ), пагинация `before_asked_at` + `limit` |
| `POST` | `/api/v1/dialogues/{dialogue_id}/reset` | Сброс контекста диалога (аналог `/reset` в боте) |
| `POST` | `/api/v1/assistant/guest/messages` | Временный диалог без БД: LLM + история в памяти процесса (`guest_session_key` от клиента) |
| `POST` | `/api/v1/assistant/guest/reset` | Сброс гостевой сессии по `guest_session_key` |
| `GET` | `/api/v1/cohorts/{cohort_id}/progress-checkpoints` | Список этапов `ProgressCheckpoint` для потока (в т.ч. `is_homework`) |
| `GET` | `/api/v1/cohorts/{cohort_id}/memberships/{membership_id}/progress-overview` | Кабинет студента: чекпоинты + свои записи прогресса по участию (роль student, MVP с общим Bearer) |
| `PUT` | `/api/v1/cohorts/{cohort_id}/memberships/{membership_id}/progress-records/{checkpoint_id}` | Upsert `ProgressRecord` по паре (участие, этап); тело может включать `submission_links` |
| `GET` | `/api/v1/cohorts/{cohort_id}/summary` | Агрегированный срез по потоку (преподаватель: участники и прогресс); query `viewer_membership_id` — участие преподавателя в этом потоке (MVP при общем Bearer) |
| `GET` | `/api/v1/cohorts/{cohort_id}/teacher-dashboard` | Панель преподавателя: KPI с недельной дельтой, ряд активности по дням, ленты Q&A и сдач, матрица; query `viewer_membership_id` — teacher |
| `GET` | `/api/v1/cohorts/{cohort_id}/leaderboard` | Лидерборд: рейтинг, поля для таблицы и scatter; query `viewer_membership_id` опционален (если передан — проверка членства в потоке) |

Детальные тела запросов/ответов — в OpenAPI YAML / `openapi.json`.

## Веб: сценарии по экранам

Сводка требований к веб-клиенту: [`docs/tech/frontend-requirements.md`](frontend-requirements.md). Ориентиры UI: [`docs/ui/ui-requirements.md`](../ui/ui-requirements.md), макеты в [`docs/tasks/tasklist-frontend.md`](../tasks/tasklist-frontend.md) (#ui-mockups). План задачи: [`docs/tasks/impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md`](../tasks/impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md).

| Экран / зона | Вызовы API (порядок) |
|--------------|----------------------|
| Вход | `POST /api/v1/auth/dev-session` → клиент сохраняет `membership_id`, `cohort_id`, роль, при необходимости `web_dialogue_id` |
| Панель преподавателя (A) | `GET .../teacher-dashboard?viewer_membership_id=...&activity_days=14` (опционально `turns_cursor`, `q` для поиска по вопросам — см. OpenAPI) |
| Лидерборд (B) | `GET .../leaderboard?...`; при необходимости заголовки колонок — `GET .../progress-checkpoints` |
| Кабинет студента (C) | `GET .../progress-overview`; сдача — `PUT .../progress-records/{checkpoint_id}` с `comment` и `submission_links` |
| Чат (D) | `GET .../dialogues/{dialogue_id}/turns`; отправка — `POST .../cohorts/{cohort_id}/dialogues/messages` с `channel: web`; сброс — `POST .../dialogues/{dialogue_id}/reset` |

## Сопоставление с доменом

| Сущность | Где в API |
|----------|-----------|
| `Cohort` | `cohort_id` в пути |
| `CohortMembership` | `membership_id` в теле (`POST ... dialogues/messages`) и в пути (progress-records) |
| `Dialogue` | создаётся/продолжается при `POST ... dialogues/messages`; `dialogue_id` в ответе и опционально в запросе |
| `DialogueTurn` | в ответе `POST .../messages` — `user_message_id`, блок `assistant_message.{id, content, created_at}`; полный список ходов — `GET .../dialogues/{dialogue_id}/turns` |
| `ProgressCheckpoint` | список в `GET ... progress-checkpoints` (поле `is_homework`), в `summary`, `teacher-dashboard`, `leaderboard`, `progress-overview` |
| `ProgressRecord` | `PUT ... progress-records/{checkpoint_id}` (`comment`, `submission_links`); фрагменты в `summary`, `teacher-dashboard`, `progress-overview` |
| `User` (вход) | `telegram_username` в теле `POST .../auth/dev-session` → идентификация пользователя и списка `memberships` |

Имена полей JSON — **snake_case**, идентификаторы — UUID.

## Статусы прогресса (enum)

`not_started`, `in_progress`, `completed`, `skipped` — см. также [`data-model.md`](../data-model.md) (сущность `ProgressRecord`).

## Идентификация (MVP)

- Заголовок: `Authorization: Bearer <token>` (схема `bearerAuth` в OpenAPI).
- На MVP токен — общий секрет клиента (бот/веб) из окружения или заглушка под будущий JWT; детали — в реализации backend и [`backend/.env.example`](../../backend/.env.example) / [`bot/.env.example`](../../bot/.env.example).
- **Веб:** после успешного `POST /api/v1/auth/dev-session` клиент передаёт в запросах тот же Bearer и явные `membership_id` / `viewer_membership_id` / `cohort_id` в путях и query, как для бота; отдельного JWT для пользователя нет.
- Сервер проверяет соответствие `membership_id` / `dialogue_id` и `cohort_id`, роли (студент / преподаватель).
- **401** — нет или неверный токен; **403** — операция запрещена для роли или ресурса.

## Ошибки

Предпочтительное тело:

```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Человекочитаемое описание",
    "details": null
  }
}
```

| HTTP | Когда |
|------|--------|
| 400 | Семантически неверный запрос (если отделён от 422) |
| 401 | Нет аутентификации |
| 403 | Нет прав |
| 404 | Ресурс не найден |
| 409 | Конфликт домена |
| 422 | Тело не проходит схему (часто ответ FastAPI по умолчанию — поле `detail`; возможна унификация в коде) |
| 502 | Проблема шлюза/ответа LLM (`LLM_BAD_GATEWAY`) |
| 503 | Провайдер LLM недоступен (`LLM_UNAVAILABLE`) |

Тексты ошибок не должны содержать содержимое переписки или внутренние трейсы ([`vision.md`](../vision.md) §15).

## Персистентность и итерации

Целевое хранение — **PostgreSQL** ([`adr/adr-001-database.md`](../adr/adr-001-database.md)). Момент подключения БД и миграций может пересекаться с итерацией «База данных» и задачей реализации backend; **HTTP-контракт не зависит** от того, in-memory или Postgres на первом шаге.

## Проверка по принципам API (`.cursor/skills/api-design-principles`)

Актуализация: сверка текста контракта и таблицы эндпоинтов со skill **api-design-principles** (роль ядра, REST, версии, ошибки, безопасность, пагинация, документация).

| Принцип | Статус | Комментарий |
|--------|--------|-------------|
| Ядро — backend; клиенты без бизнес-логики | OK | Заложено в [`vision.md`](../vision.md); бизнес-правила и LLM не выносятся в бот/веб. |
| Один контракт для каналов; без «только для Telegram» | OK | Поле `channel` (`telegram` / `web`) общее; ответы не завязаны на один канал. Опциональный `web_dialogue_id` в `dev-session` — снижение round-trip для веба, не дублирование правил. |
| Ресурсы — существительные, мн. ч.; глаголы через HTTP | Частично | `cohorts`, `dialogues`, `messages`, `progress-checkpoints`, `progress-records`, `memberships` — ок. Процедурные сегменты: `POST .../dialogues/{id}/reset`, `POST .../auth/dev-session`, `POST .../assistant/guest/messages` — допустимы при явном описании в OpenAPI; при смене мажорной версии можно заменить на ресурсные модели (`PATCH` диалога, `POST .../sessions` и т.д.). |
| Вложенность путей по иерархии | OK | `cohort → memberships → progress-records` и `cohort → dialogues → messages` отражают домен. Агрегаты чтения `teacher-dashboard`, `leaderboard`, `progress-overview` — подресурсы представления потока/участия, глубина оправдана. |
| Версия в пути `/api/v1/`, ломающие изменения только в новой мажорной версии | OK | Зафиксировано выше; расширение схем ответов — только необязательные поля в рамках v1. |
| Успех: стабильная JSON-схема; ошибки: единый формат; без трейсов клиенту | Частично | В skill в примере ошибки фигурирует корневой `detail`; в проекте предпочтительно тело с `error.{code,message,details}` (см. §«Ошибки»). Нужна последовательность: **422** от FastAPI часто с `detail` — либо унификация в коде под тот же контракт, либо явная оговорка для клиентов в OpenAPI. Утечки переписки/трейсов — запрещены ([`vision.md`](../vision.md) §15). |
| Коды HTTP | OK | 400/401/403/404/409/422 и 502/503 для LLM согласованы со skill. |
| Аутентификация и роли в контракте | OK | `bearerAuth`; 401/403; явные `membership_id` / `viewer_membership_id` / `cohort_id`; проверка соответствия сущностей на сервере. |
| Пагинация/фильтры для списков | OK | Для списков ходов — `limit`, `before_asked_at` / cursor в OpenAPI; лента на `teacher-dashboard` — `turns_cursor`, `q`, `limit`. Списки чекпоинтов и `summary` без пагинации на MVP при малом объёме — оговорено; при росте данных — только необязательные параметры или v2. |
| OpenAPI — источник правды для публичных маршрутов | OK | YAML + приоритет `openapi.json` после scaffold; новые пути описаны в YAML. |

## Связанные документы

- [`docs/integrations.md`](../integrations.md) — обзор клиент → backend
- [`docs/api/openapi-v1.yaml`](../api/openapi-v1.yaml) — машиночитаемый черновик
- План исходных контрактов: [`docs/tasks/impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md`](../tasks/impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md)
- План веб-контрактов (итерация 4): [`docs/tasks/impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md`](../tasks/impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md)
