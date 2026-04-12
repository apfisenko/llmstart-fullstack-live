# Задача 05: итог

## Сделано

- **ORM:** `DialogueTurn` / `dialogue_turns`; удалены `DialogueMessage`, `MessageRole`; `Dialogue.turns` с сортировкой по `asked_at`.
- **Миграция:** [`backend/migrations/versions/0004_dialogue_turns.py`](../../../../../../../backend/migrations/versions/0004_dialogue_turns.py) — перенос пар из `dialogue_messages` при наличии; если таблица `dialogue_turns` уже создана `create_all` на шаге `0001`, перенос только дропает `dialogue_messages` при её наличии.
- **Сервисы:** [`dialogue_service.py`](../../../../../../../backend/app/services/dialogue_service.py) пишет одну строку на Q/A; [`cohort_service.py`](../../../../../../../backend/app/services/cohort_service.py) через репозиторий.
- **Репозитории:** [`DialogueRepository`](../../../../../../../backend/app/infrastructure/repositories/dialogue_repository.py), [`CohortProgressRepository`](../../../../../../../backend/app/infrastructure/repositories/cohort_progress_repository.py).
- **Документация:** `docs/data-model.md` (блок «Соответствие реализации»), `docs/api/openapi-v1.yaml`, `docs/tech/db-tooling-guide.md`, `docs/tech/api-contracts.md`.
- **Makefile:** `backend-test`, `backend-dev`, `backend-lint`, `backend-typecheck` (mypy не настроен — сообщение в цели).

## Отклонения / решения

- **GuestDialogueService:** история по-прежнему в памяти процесса — по продуктовой модели «гость вне потока»; не относится к персистентности когортных диалогов.
- **mypy:** не добавлялся в `pyproject.toml`; DoD по typecheck закрыт пояснением в `make backend-typecheck`.
- **Локальный Postgres:** проверено: Docker Compose в WSL, `alembic upgrade head` и `alembic current` с Windows (`DATABASE_URL` → `127.0.0.1:5432`) — цепочка до **`0004_dialogue_turns (head)`**; затем `pytest` после сброса `DATABASE_URL` (SQLite in-memory) — 24 passed. Сценарий задокументирован в [`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md) («Смешанный режим»), цель **`make db-migrate-test`** в корневом [`Makefile`](../../../../../../../Makefile).

## Pytest (`uv run pytest tests/`)

| Тест | Результат |
|------|-----------|
| test_health_ok | PASSED |
| test_post_dialogue_message_returns_assistant_reply | PASSED |
| test_post_dialogue_message_unknown_cohort_uses_ephemeral_llm | PASSED |
| test_post_dialogue_message_unknown_cohort_continues_with_dialogue_id | PASSED |
| test_post_dialogue_message_unknown_cohort_foreign_dialogue_id_forbidden | PASSED |
| test_post_dialogue_message_unknown_cohort_wrong_dialogue_id_forbidden | PASSED |
| test_post_dialogue_message_continues_same_dialogue_id | PASSED |
| test_post_dialogue_message_validation_422 | PASSED |
| test_post_dialogue_message_unauthorized_wrong_bearer | PASSED |
| test_post_dialogue_message_unauthorized_missing_bearer | PASSED |
| test_v1_allowed_without_bearer_when_token_not_configured | PASSED |
| test_llm_failure_returns_503 | PASSED |
| test_dialogue_reset_returns_204 | PASSED |
| test_dialogue_reset_clears_history_for_next_message | PASSED |
| test_post_message_logs_do_not_contain_user_text | PASSED |
| test_post_guest_message_ok | PASSED |
| test_post_guest_reset_clears_session | PASSED |
| test_wrong_membership_for_dialogue_forbidden | PASSED |
| test_list_progress_checkpoints_ok | PASSED |
| test_list_progress_checkpoints_not_found | PASSED |
| test_put_progress_record_ok | PASSED |
| test_put_progress_teacher_forbidden | PASSED |
| test_get_summary_as_teacher | PASSED |
| test_get_summary_student_forbidden | PASSED |

**Итого:** 24 passed.

## Линт

- `ruff check app tests` и `ruff format app tests` — без замечаний после правок.
