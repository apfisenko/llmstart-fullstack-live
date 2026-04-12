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

Служебные маршруты вне контракта v1: например `GET /health`, документация OpenAPI — см. задачу scaffold backend.

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/api/v1/cohorts/{cohort_id}/dialogues/messages` | Сообщение в диалог: создать/продолжить `Dialogue`, сохранить ход (`DialogueTurn`), вызвать LLM, вернуть ответ ассистента |
| `POST` | `/api/v1/dialogues/{dialogue_id}/reset` | Сброс контекста диалога (аналог `/reset` в боте) |
| `POST` | `/api/v1/assistant/guest/messages` | Временный диалог без БД: LLM + история в памяти процесса (`guest_session_key` от клиента) |
| `POST` | `/api/v1/assistant/guest/reset` | Сброс гостевой сессии по `guest_session_key` |
| `GET` | `/api/v1/cohorts/{cohort_id}/progress-checkpoints` | Список этапов `ProgressCheckpoint` для потока |
| `PUT` | `/api/v1/cohorts/{cohort_id}/memberships/{membership_id}/progress-records/{checkpoint_id}` | Upsert `ProgressRecord` по паре (участие, этап) |
| `GET` | `/api/v1/cohorts/{cohort_id}/summary` | Агрегированный срез по потоку (преподаватель: участники и прогресс); query `viewer_membership_id` — участие преподавателя в этом потоке (MVP при общем Bearer) |

Детальные тела запросов/ответов — в OpenAPI YAML / `openapi.json`.

## Сопоставление с доменом

| Сущность | Где в API |
|----------|-----------|
| `Cohort` | `cohort_id` в пути |
| `CohortMembership` | `membership_id` в теле (`POST ... dialogues/messages`) и в пути (progress-records) |
| `Dialogue` | создаётся/продолжается при `POST ... dialogues/messages`; `dialogue_id` в ответе и опционально в запросе |
| `DialogueTurn` | в ответе — `user_message_id` (= `id` хода), блок `assistant_message.{id, content, created_at}` (= `assistant_message_id` и метаданные ответа) |
| `ProgressCheckpoint` | список в `GET ... progress-checkpoints` и в ответе `summary` |
| `ProgressRecord` | `PUT ... progress-records/{checkpoint_id}` и данные в summary |

Имена полей JSON — **snake_case**, идентификаторы — UUID.

## Статусы прогресса (enum)

`not_started`, `in_progress`, `completed`, `skipped` — см. также [`data-model.md`](../data-model.md) (сущность `ProgressRecord`).

## Идентификация (MVP)

- Заголовок: `Authorization: Bearer <token>` (схема `bearerAuth` в OpenAPI).
- На MVP токен — общий секрет клиента (бот/веб) из окружения или заглушка под будущий JWT; детали — в реализации backend и `.env.example`.
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

| Принцип | Статус | Комментарий |
|--------|--------|-------------|
| Ядро — backend; клиенты без бизнес-логики | OK | Заложено в [`vision.md`](../vision.md); поля контракта канал-агностичны (нет полей «только для Telegram»). |
| Ресурсы — существительные, мн. ч.; глаголы через HTTP | Частично | `cohorts`, `dialogues`, `messages`, `progress-checkpoints`, `progress-records` — ок. `POST .../reset` — процедурный подресурс (сброс состояния); допустимо при явном описании, альтернатива — смена состояния через `PATCH` диалога в будущей версии. |
| Вложенность путей по иерархии | OK | `cohort → memberships → progress-records` отражает домен. |
| Версия в пути `/api/v1/`, ломающие изменения только в новой мажорной версии | OK | Зафиксировано выше. |
| Успех: стабильная JSON-схема; ошибки: единый формат; без трейсов клиенту | OK | Обёртка `error`; оговорка про `422`/`detail` FastAPI; запрет утечки переписки — см. [`vision.md`](../vision.md) §15. |
| Коды HTTP | OK | 4xx/409/422 и отдельно 502/503 для LLM согласованы со skill (валидация/доступ/конфликт; 5xx при сбоях зависимостей). |
| Аутентификация и роли в контракте | OK | Bearer; 401/403; проверка `membership`/`cohort`. |
| Пагинация/фильтры для списков | Зафиксировано | На MVP списки этапов (`progress-checkpoints`) и состав `summary` могут быть без пагинации при малом объёме. При росте данных — добавить `limit`/`offset` или cursor **в той же версии только как необязательные поля** или вынести в v2 по правилам версионирования; детали — в OpenAPI при расширении. |
| OpenAPI — источник правды для публичных маршрутов | OK | Ссылка на YAML / `openapi.json` в начале документа. |

## Связанные документы

- [`docs/integrations.md`](../integrations.md) — обзор клиент → backend
- [`docs/api/openapi-v1.yaml`](../api/openapi-v1.yaml) — машиночитаемый черновик
- План задачи: [`docs/tasks/impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md`](../tasks/impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md)
