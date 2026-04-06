# Задача 02: Проектирование API-контрактов — summary

## Результат

- Зафиксирован черновик OpenAPI v1: **[docs/api/openapi-v1.yaml](../../../../../../api/openapi-v1.yaml)**.
- Описание ресурсов, ошибок, MVP-аутентификации и согласование с DoD итерации 2 — в **[plan.md](plan.md)**.
- Обновлены **[docs/integrations.md](../../../../../../integrations.md)** (раздел «Backend HTTP API»), **[docs/data-model.md](../../../../../../data-model.md)** (enum статусов `ProgressRecord` для API), **[docs/plan.md](../../../../../../plan.md)** (итерация 2: доменные имена, персистентность vs итерация 3).

## Отклонения / решения

- **Источник правды:** после scaffold приоритет у `GET /openapi.json`; YAML остаётся контрактной опорой и должен синхронизироваться при существенных расхождениях (задачи 05–06).
- **Ошибки:** целевой формат `{"error": { "code", "message", "details" }}`; FastAPI по умолчанию отдаёт `422` с `detail` — унификация в задаче 05 по необходимости.
- **DoD «Submission»:** в документации заменено на **`ProgressRecord`** в терминах `data-model.md`.

## Где смотреть

| Артефакт | Путь |
|----------|------|
| OpenAPI v1 (черновик) | `docs/api/openapi-v1.yaml` |
| Сводка контракта (человекочитаемо) | `docs/tech/api-contracts.md` |
| План задачи | `docs/tasks/impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md` |
