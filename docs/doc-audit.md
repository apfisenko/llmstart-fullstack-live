# Аудит документации и онбординга

**Цель:** чтобы человек или AI-агент мог войти в репозиторий, понять границы системы, поднять окружение и проверить работоспособность за один сеанс.

**Дата фиксации аудита:** 2026-04-17.

**Связанные артефакты:** [README.md](../README.md), [docs/onboarding.md](onboarding.md), [docs/architecture.md](architecture.md), [docs/plan.md](plan.md), [docs/vision.md](vision.md), [docs/data-model.md](data-model.md), [docs/tech/api-contracts.md](tech/api-contracts.md), [Makefile](../Makefile), [tasks.ps1](../tasks.ps1), [backend/README.md](../backend/README.md), [bot/README.md](../bot/README.md), [frontend/web/README.md](../frontend/web/README.md), [frontend/web/.gitignore](../frontend/web/.gitignore), [.github/workflows/ci.yml](../.github/workflows/ci.yml).

---

## Статус плана P0–P2 (закрыто)

| Уровень | Итог |
|---------|------|
| **P0** | Диаграмма в README: `bot/` вместо `frontend/bot`. |
| **P1** | Шаблон `frontend/web/.env.example` в репо; README веба и [bot/README.md](../bot/README.md); ссылки на корневой `.env.example` убраны из актуальных docs/tasklists и правок в `docs/tasks/impl/**` по согласованию с аудитом. |
| **P2** | Таблица версий и `make ci-check` / `.\tasks.ps1 ci-check`; явно про отсутствие `pnpm test`; [onboarding.md](onboarding.md), [architecture.md](architecture.md); [AGENTS.md](../frontend/web/AGENTS.md); роль [data/README.md](../data/README.md) в корневом README. |

**Остаток:** в [`.cursor/plans/`](../.cursor/plans/) могут остаться исторические черновики со ссылкой на корневой `.env.example` — не входят в онбординг; при редактировании ориентироваться на компонентные шаблоны.

---

## Приоритезированный план устранения пробелов (архив исходного аудита)

Ниже — исходная формулировка; выполнение см. раздел «Статус плана P0–P2» выше.

### P0 — блокеры запуска и доверия к инструкциям

| # | Действие | Обоснование |
|---|----------|-------------|
| P0.1 | Исправить диаграмму в [README.md](../README.md): `frontend/bot` → `bot/` (фактическая структура репо). | Неверный путь вводит в заблуждение при навигации. |

### P1 — целостность ссылок и компонентных README

| # | Действие | Обоснование |
|---|----------|-------------|
| P1.1 | Удалить во всех документах ссылки на **корневой** `.env.example`. Шаблоны окружения — только у компонентов: [`backend/.env.example`](../backend/.env.example), [`bot/.env.example`](../bot/.env.example), [`frontend/web/.env.example`](../frontend/web/.env.example). | Корневого файла нет и не предполагается; ссылки вводят в заблуждение. |
| P1.2 | Заменить [frontend/web/README.md](../frontend/web/README.md) с шаблона create-next-app на описание проекта LLMStart. | Единственный README компонента не отражает монорепо. |
| P1.3 | Добавить [bot/README.md](../bot/README.md). | Нет точки входа «только бот» для новичка/агента. |

### P2 — один happy-path, качество как в CI, агенты

| # | Действие | Обоснование |
|---|----------|-------------|
| P2.1 | В корневом README и Makefile: полная статическая проверка как в CI (`ci-check`). | `make lint` без ESLint фронта. |
| P2.2 | Таблица версий / отсылка к `ci.yml`. | Снижает расхождение с CI. |
| P2.3 | Явно: юнит-тестов фронта нет; `pnpm lint` + `pnpm build`. | Избегает `pnpm test`. |
| P2.4 | [onboarding.md](onboarding.md), happy-path в README. | Первый успешный прогон. |
| P2.5 | [frontend/web/AGENTS.md](../frontend/web/AGENTS.md). | Граф знаний для агента. |
| P2.6 | Роль [data/README.md](../data/README.md) в корневом README. | Меньше путаницы с приложением. |

---

## Шаг 1. Реестр ключевой документации

Статусы: **актуально** / **устарело** / **отсутствует** / **другое назначение**.

| Файл | Описание | Статус | Проблемы |
|------|----------|--------|----------|
| [README.md](../README.md) | Точка входа, ссылки на architecture / onboarding / plan | Актуально | — |
| [docs/onboarding.md](onboarding.md) | Пошаговый онбординг | Актуально | — |
| [docs/architecture.md](architecture.md) | Обзор компонентов и mermaid | Актуально | — |
| [backend/README.md](../backend/README.md) | uvicorn, БД, pytest | Актуально | При правках Settings сверять с `backend/.env.example`. |
| [bot/README.md](../bot/README.md) | Запуск бота из корня | Актуально | — |
| [frontend/web/README.md](../frontend/web/README.md) | Веб в монорепо, pnpm, env, smoke | Актуально | — |
| [data/README.md](../data/README.md) | Программа курса | Другое назначение | Не документация приложения. |
| [docs/vision.md](vision.md) | Границы системы | Актуально | Ссылка на onboarding/architecture. |
| [docs/plan.md](plan.md) | Дорожная карта | Актуально | Канон статусов итераций. |
| [docs/data-model.md](data-model.md) | Сущности, API | Актуально | Для быстрого старта — [onboarding.md](onboarding.md) §4. |
| [docs/tech/api-contracts.md](tech/api-contracts.md) | Сводка HTTP v1 | Актуально | OpenAPI / `/openapi.json`. |
| [docs/integrations.md](integrations.md) | Интеграции, секреты | Актуально | — |
| [docs/tech/db-tooling-guide.md](tech/db-tooling-guide.md) | Docker, WSL, Alembic | Актуально | См. onboarding. |
| [docs/adr/](adr/) | ADR | Актуально | После vision. |
| [backend/.env.example](../backend/.env.example) | Шаблон backend | Ожидается актуально | — |
| [bot/.env.example](../bot/.env.example) | Шаблон бота | Ожидается актуально | — |
| [frontend/web/.env.example](../frontend/web/.env.example) | Шаблон → `.env.local` | Актуально | В репозитории; `.gitignore` игнорирует только `.env.local`. |
| Корневой `.env.example` | Не используется | Отсутствует (намеренно) | Не добавлять. |
| [Makefile](../Makefile) | В т.ч. `ci-check` | Актуально | Полная статика: `make ci-check`. |
| [tasks.ps1](../tasks.ps1) | Windows-аналог | Актуально | `ci-check` в help. |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | CI | Актуально | Канон порядка шагов. |
| [.cursor/rules/](.cursor/rules/) | workflow, conventions | Актуально | См. onboarding §5. |
| [frontend/web/AGENTS.md](../frontend/web/AGENTS.md) | Агенты Next + ссылки на docs | Актуально | — |
| [docs/idea.md](idea.md), [docs/tasks/](tasks/) | Продукт, задачи | Актуально / архив | В `impl/**` summary могут описывать прошлое состояние репо. |

---

## Шаг 2. Аудит «запускаемости» (один сеанс)

| Пункт | Статус | Комментарий |
|--------|--------|-------------|
| Установка системных зависимостей | **Есть** | Таблица в README + `ci.yml`. |
| Настройка окружения | **Есть** | Три шаблона: `backend/`, `bot/`, `frontend/web/`. |
| Запуск базы данных | **Есть** | `db-up`, db-tooling-guide. |
| Запуск backend | **Есть** | README, onboarding. |
| Запуск frontend | **Есть** | `.env.example`, README веба, onboarding. |
| Запуск бота | **Есть** | bot/README, корневой README. |
| Запуск тестов | **Есть** | Backend: `test-backend`; фронт без `pnpm test` — задокументировано. |
| Проверка работоспособности | **Есть** | `/health`, dev-session, onboarding §3. |
| Проверка качества кода | **Есть** | `make ci-check` + `make test-backend`; `backend-typecheck` — заглушка (без изменения контракта Makefile). |

**Краткий вывод:** чеклист закрыт документацией P0–P2; повторный проход при крупных изменениях в CI или структуре репо — обновить README, [onboarding.md](onboarding.md) и при необходимости [technical-debt.md](tech/technical-debt.md).

---

## Критические расхождения (сводка) — сняты

Ранее зафиксированные расхождения (README vs plan, mermaid, env веба, корневой `.env.example`, `make lint` vs CI) устранены в рамках плана 2026-04-17. Актуальный перечень рисков ведётся в [docs/tech/technical-debt.md](tech/technical-debt.md) при появлении новых долгов.
