# План: задача 08 — базовое качество (линт, тесты, CI, Makefile)

## Цель

Единые команды качества в корне репозитория, воспроизводимая установка зависимостей, минимальный CI; документация согласована с `Makefile`.

## Состав работ

1. **`Makefile`:** `install` — `uv sync --group dev` в корне и `uv sync --extra dev` в `backend/`; `lint` / `format` — `bot/` через корневой `uv run ruff`, затем `backend/app` и `backend/tests` через `backend` venv; `test` — алиас на `test-backend` (pytest в `backend/`); `run` — `uv run python -m bot.main`.
2. **CI:** `.github/workflows/ci.yml` — на `push`/`pull_request` в `main`/`master`: те же шаги, что линт + тест.
3. **Документация:** [README.md](../../../../../../../README.md) — таблица без make, блок перед PR, ссылка на CI; [docs/plan.md](../../../../../../../docs/plan.md) — итерация 2 завершена; [docs/vision.md](../../../../../../../docs/vision.md) §10 — пункт про локальную проверку и CI.
4. **Ретроспектива API:** отдельный файл версионирования не вводить при отсутствии дублирования; зафиксировать в summary.

## DoD

- После `make install`: `make lint` и `make test` — код 0.
- README и Makefile согласованы.
- CI зелёный или явная локальная договорённость (оба выполнены: CI + README).

## Связанные документы

- [tasklist-backend.md](../../../../../tasklist-backend.md) — блок 6.
- Skills: `python-testing-patterns` при доработке pytest в CI (не обязательно).
