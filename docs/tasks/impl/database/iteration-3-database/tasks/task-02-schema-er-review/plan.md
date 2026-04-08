# Задача 02: схема данных — логика, физика, ER, ревью

## Контекст

- **Сценарии и требования к данным:** [`docs/tech/user-scenarios.md`](../../../../../../tech/user-scenarios.md) (задача 01).
- **Контракт API:** [`docs/api/openapi-v1.yaml`](../../../../../../api/openapi-v1.yaml) — имена `Cohort`, `ProgressCheckpoint`, пути `/cohorts/...`.
- **Сид:** [`data/progress-import.v1.json`](../../../../../../../data/progress-import.v1.json) — `telegram_id`, `lesson_position` → порядок чекпоинта.
- **Ревью схемы:** skill `postgresql-table-design` (`.cursor/skills/postgresql-table-design/SKILL.md`).

Источник состава работ и DoD: [`docs/tasks/tasklist-database.md`](../../../../../../tasks/tasklist-database.md), блок 2.

## Цель

Упростить и актуализировать модель данных под учебный этап: допущения «модуль == урок» и пары «вопрос + ответ»; обновить [`docs/data-model.md`](../../../../../../data-model.md) (логика + физика PostgreSQL + Mermaid ER); провести ревью по чеклисту skill и зафиксировать решения.

## План работ

1. Зафиксировать **имена таблиц** в соответствии с OpenAPI: `cohorts`, `cohort_memberships`, `progress_checkpoints` (не отдельное имя `lessons` без связи с API), `users`, `dialogues`, `dialogue_turns`, `progress_records`; явная таблица сопоставления домен ↔ API ↔ БД.
2. **Логическая модель:** описать `ProgressCheckpoint` как единый уровень «урок программы потока»; ввести `DialogueTurn` вместо пары сущностей сообщений как основу хранения; добавить признак ДЗ (`is_homework`); уточнить `User` (в т.ч. `telegram_id` под импорт).
3. **Физическая модель:** типы PostgreSQL, PK/FK и `ON DELETE`, UNIQUE, частичные индексы (активный диалог, уникальный `telegram_id`), ENUM-типы, согласованные со значениями API.
4. **Mermaid ER** по таблицам с типами колонок и пометками PK/FK.
5. Подраздел **«Результат ревью (postgresql-table-design)»** — таблица решений по чеклисту skill.
6. Согласовать формулировку про ДЗ в `user-scenarios.md` с обновлённой моделью.
7. Самопроверка по DoD блока 2 в `tasklist-database.md`.

## Критерии готовности (DoD)

- `docs/data-model.md` отражает актуальный набор сущностей и таблиц, допущения учебного этапа и покрытие сценариев задачи 01.
- Физическая ER-диаграмма (Mermaid) содержит таблицы, типы, PK/FK; ограничения и индексы описаны в тексте.
- Ревью по `postgresql-table-design` отражено в документе (принятые решения).

## Связанные задачи

- **До:** задача 01 (`user-scenarios.md`).
- **После:** задача 03 (ADR и справка по tooling), задача 04 (миграции по этой схеме).
