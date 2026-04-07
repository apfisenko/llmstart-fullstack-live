# Summary: задача 08 — базовое качество

## Сделано

- **[Makefile](../../../../../../../Makefile):** `install` через `uv` (корень + `backend` dev); `lint` / `format` — последовательно `bot/` и `backend/app`, `backend/tests`; добавлена цель **`test`** как алиас **`test-backend`**; `run` через `uv run python -m bot.main`.
- **CI:** [`.github/workflows/ci.yml`](../../../../../../../.github/workflows/ci.yml) — lint + pytest на Ubuntu для веток `main`/`master` и PR.
- **Согласование ruff:** в корневом [pyproject.toml](../../../../../../../pyproject.toml) добавлен `ignore = ["UP045"]` (как в backend); в [backend/pyproject.toml](../../../../../../../backend/pyproject.toml) — `line-length = 100`; прогон `ruff format` на затронутых файлах backend и bot.
- **Документация:** [README.md](../../../../../../../README.md), [backend/README.md](../../../../../../../backend/README.md), [docs/plan.md](../../../../../../../plan.md), [docs/vision.md](../../../../../../../vision.md) §10, [tasklist-backend.md](../../../../../tasklist-backend.md).

## Отклонения / решения

- **Версионирование API:** отдельный `docs/tech/api-versioning.md` не создавался — правила уже сжато в [`docs/integrations.md`](../../../../../../../docs/integrations.md) и OpenAPI; дублирование не оправдано.
- **§11 vision:** без изменений — новые практики не затрагивают данные и состояние.

## Проверка

- `uv sync --group dev`, `cd backend && uv sync --extra dev`, затем команды из целей `lint` и `pytest` — успех локально (Windows).
- После пуша ожидается зелёный workflow **CI** на GitHub.
