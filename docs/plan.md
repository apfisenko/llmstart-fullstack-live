# Дорожная карта

## Организация работ

Этот документ — единая сквозная дорожная карта: каждый этап соответствует итерации, реализуемой через отдельный **tasklist** по области. Детализация задач, планов и итогов ведётся в `docs/tasks/tasklist-<область>.md` согласно [workflow](.cursor/rules/workflow.mdc); `plan.md` фиксирует только цели, порядок и критерии завершения итераций. Принцип «один этап — один основной tasklist» определяет, в каком файле ведётся приоритетная область работ.

---

## Ключевые особенности плана

**Backend-first / одно ядро.** Бизнес-правила, работа с данными и LLM живут в `backend/`; бот и веб — тонкие клиенты без уникальной логики. Это предотвращает дублирование и позволяет любому новому клиенту сразу получать полные возможности платформы.

**API-first для клиентов.** Контракт HTTP API backend стабилизируется прежде, чем начинается масштабная работа над веб-интерфейсом. Это позволяет вести разработку бота и веб-клиента независимо от внутреннего устройства ядра.

**Поэтапная ценность: бот → веб.** Первые итерации дают работающий сценарий сопровождения через Telegram; затем те же смыслы переносятся в веб-кабинет — без смены продуктовой идеи, только расширение канала.

---

## Легенда статусов

📋 Planned — запланирован &nbsp; 🚧 In Progress — в работе &nbsp; ✅ Done — завершён

---

## Обзор итераций

| Итерация | Название | Цель | Статус | Tasklist |
|----------|----------|------|--------|----------|
| 1 | MVP: Telegram-бот | Рабочий бот с LLM, история в памяти | ✅ Done | см. примечание ниже |
| 2 | Backend API | Полный API: scaffold, LLM, прогресс, поток | ✅ Done | [tasklist-backend](tasks/tasklist-backend.md) |
| 3 | База данных | PostgreSQL, схема, миграции | ✅ Done | [tasklist-database](tasks/tasklist-database.md) |
| 4 | Реализация Frontend | Веб-кабинет студента и преподавателя | ✅ Done | [tasklist-frontend](tasks/tasklist-frontend.md) |
| 5 | Интеграция клиентов | Бот и веб работают через backend API | ✅ Done | [tasklist-backend](tasks/tasklist-backend.md) (задача 07) + [tasklist-frontend](tasks/tasklist-frontend.md) |
| 6 | Dev&Ops & Production | CI/CD, контейнеризация, production-deploy | ✅ Done | [tasklist-devops](tasks/tasklist-devops.md) |

**Примечание к ссылкам:** отдельный файл `docs/tasks/tasklist-bot.md` в репозитории пока не ведётся. Итерация **1:** код и сценарии — каталог [`bot/`](../bot/). Итерация **5 (продукт):** закрыта по DoD в [`plan.md`](plan.md) §итерация 5 — бот через API ([tasklist-backend](tasks/tasklist-backend.md), задача **07**), веб на **`/api/v1/`** ([tasklist-frontend](tasks/tasklist-frontend.md)). Итерация **6 (Dev&Ops):** [tasklist-devops](tasks/tasklist-devops.md) — локальный compose, GHCR, VPS, [vps-manual-ghcr-deploy.md](tech/vps-manual-ghcr-deploy.md), [автодеплой](tasks/tasklist-devops.md#iteration-5-cd-gha) (job **deploy** в [`.github/workflows/ghcr.yml`](../.github/workflows/ghcr.yml), [docker-compose-ghcr.md § CD](tech/docker-compose-ghcr.md#cd-автодеплой-github-actions)); CI — [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

---

## Итерации

---

### Итерация 1: MVP — Telegram-бот ✅

**Цель:** запустить рабочего Telegram-бота с диалогом через LLM в рамках курса.

**Критерии завершения (DoD):**

- Бот принимает сообщения, отвечает через LLM (OpenRouter-совместимый провайдер).
- История диалога хранится в памяти процесса (`dict[int, list[dict]]`).
- Конфигурация через `.env`; логирование без текста переписки.
- Структура `bot/` соответствует конвенциям проекта.

**Связь с tasklist:** отдельного `tasklist-bot.md` нет — ориентир по коду: [`bot/`](../bot/).

**Полезный результат:** участники курса могут задавать вопросы ассистенту в Telegram.

**Артефакты:** `bot/` (`main.py`, `config.py`, `handlers/`, `services/backend_assistant.py`).

---

### Итерация 2: Backend API ✅

**Цель:** реализовать полный backend API — структура проекта, конфигурация, диалог с LLM, прогресс и поток.

**Статус по [tasklist-backend](tasks/tasklist-backend.md):** итерация **2** (Backend API в смысле `plan.md`) закрыта задачами **01–06** и **08** (в т.ч. линт, тесты, GitHub Actions CI, `Makefile`). Задача **07** (бот как клиент API) закрыта и входит в **итерацию 5** ниже — **✅ Done**.

**Критерии завершения (DoD):**

- Структура `backend/` создана, соответствует целевой раскладке из [`vision.md`](vision.md).
- Backend стартует, читает конфиг из `.env`, падает с понятной ошибкой при неполной конфигурации.
- Доступен health-эндпоинт; проект проходит линт и базовые тесты.
- Backend принимает запрос диалога, обращается к LLM (OpenRouter-совместимый провайдер) и возвращает ответ.
- История диалога (`Dialogue`, `DialogueMessage`) сохраняется в **PostgreSQL** (не в памяти процесса backend). Порядок подключения БД и миграций может пересекаться с [итерацией 3](tasks/tasklist-database.md) и задачами [tasklist-backend](tasks/tasklist-backend.md); HTTP-контракт v1 ([`docs/api/openapi-v1.yaml`](api/openapi-v1.yaml)) не зависит от момента включения персистентности.
- Сбои LLM-провайдера обрабатываются централизованно: понятный ответ клиенту + логирование без текста переписки.
- Сущности прогресса из [`data-model.md`](data-model.md) — **`ProgressCheckpoint`** и **`ProgressRecord`** — существуют в схеме и доступны через API (в DoD ранее использовались имена Progress / Submission как ориентир).
- Эндпоинт фиксации результата принимает и сохраняет отметку студента.
- API возвращает агрегированный срез по потоку (статус участников).
- Контракт API задокументирован (схемы запросов/ответов).

**Связь с tasklist:** [docs/tasks/tasklist-backend.md](tasks/tasklist-backend.md)

**Полезный результат:** backend API полностью готов — клиенты (бот, веб) могут подключаться без доработок ядра.

**Артефакты:** `backend/app/`, [`backend/.env.example`](../backend/.env.example), API-контракт для клиентов.

---

### Итерация 3: База данных ✅

**Статус по [tasklist-database](tasks/tasklist-database.md):** задачи **01–05** закрыты; итерация 3 считается **завершённой** по факту tasklist (сводный `summary.md` уровня итерации при необходимости — в `docs/tasks/impl/database/iteration-3-database/`).

**Цель:** персистентный слой на PostgreSQL для всего домена API v1: пользователи, потоки, участия, диалоги и сообщения, этапы и записи прогресса; воспроизводимые миграции; локальная инфраструктура (Docker) и начальное наполнение из выгрузки `data/progress-import.v1.json`; документация сценариев «студент / преподаватель → данные» и операционная справка по БД.

**Критерии завершения (DoD):**

- PostgreSQL — целевая среда для локальной разработки и проверок; поднимается из репозитория (например `docker-compose`); соединение валидируется при старте backend.
- Таблицы по [`data-model.md`](data-model.md) (включая `Dialogue`, `DialogueTurn` / `dialogue_turns`, `ProgressCheckpoint`, `ProgressRecord` и базовые `User`, `Cohort`, `CohortMembership`) существуют, согласованы с ORM и **переживают рестарт** БД и приложения.
- Миграции Alembic **воспроизводимы с нуля** одной цепочкой команд; политика и команды задокументированы в ADR по tooling (см. [задачу 03](tasks/tasklist-database.md) в `tasklist-database.md`, файл `docs/adr/adr-004-db-tooling.md`) и в [`docs/tech/db-tooling-guide.md`](tech/db-tooling-guide.md).
- ADR-001 и ADR-002 отражены на практике; принят ADR по операциям с БД и инструментам (**`docs/adr/adr-004-db-tooling.md`**, dev/CI, миграции, соотношение с SQLite в тестах при необходимости).
- `Makefile`: как минимум `db-up`, `db-down`, `db-reset`, `db-shell`, `migrate-backend`, `seed-progress` или `db-seed` — задокументированы в README и в [`docs/tech/db-tooling-guide.md`](tech/db-tooling-guide.md).
- Начальное наполнение из `data/progress-import.v1.json` выполняется командой сида; схема JSON описана в плане задачи 04 tasklist.
- Backend API v1 при работе с персистентными сущностями использует PostgreSQL (не файл SQLite по умолчанию для dev); гостевой ассистент без БД — по контракту без изменений.
- Актуализированы: [`docs/tasks/tasklist-database.md`](tasks/tasklist-database.md) (итерация закрыта), [`docs/data-model.md`](data-model.md), при необходимости OpenAPI/контракт; DoD этого раздела сверяется с `summary.md` итерации в `docs/tasks/impl/database/iteration-3-database/`.

**Связь с tasklist:** [docs/tasks/tasklist-database.md](tasks/tasklist-database.md)

**Полезный результат:** слой данных готов; клиенты получают стабильное хранилище под сценарии студента и преподавателя.

**Артефакты:** `docker-compose.yml` (или эквивалент), `backend/migrations/`, `backend/app/domain/`, `backend/app/infrastructure/`, `data/progress-import.v1.json`, скрипт/команда сида, обновлённые `Makefile`, `backend/.env.example`, `docs/tech/user-scenarios.md`, `docs/tech/db-tooling-guide.md`, `docs/adr/adr-004-db-tooling.md`.

---

### Итерация 4: Реализация Frontend ✅

**Статус по [tasklist-frontend](tasks/tasklist-frontend.md):** задачи **01–08** закрыты (MVP веб-клиента). Задачи **09–10** (голос, Text-to-SQL) **не выполняются** (⛔), зафиксировано в [`docs/tech/technical-debt.md`](tech/technical-debt.md) §«Отложенное развитие» — на цели итерации 4 (студент / преподаватель / чат по API) не влияют.

**Цель:** создать единый веб-клиент с двумя ролями: кабинет студента и интерфейс преподавателя.

⚡ **Параллельность:** можно начинать параллельно с завершением итерации 2, если API-контракт зафиксирован (основание: клиенты — адаптеры, `vision.md §2`).

**Критерии завершения (DoD):**

- **Студент:** навигация по программе, просмотр своего прогресса, диалог с ассистентом.
- **Преподаватель:** список участников потока, агрегированный срез активности группы.
- Роли разграничены на уровне UI и маршрутизации; веб-клиент не дублирует логику backend.
- Ключевые сценарии из [`idea.md`](idea.md) реализованы в интерфейсе.

**Связь с tasklist:** [docs/tasks/tasklist-frontend.md](tasks/tasklist-frontend.md)

**Полезный результат:** студент и преподаватель работают с платформой через браузер.

**Артефакты:** `frontend/web/` (единый проект), конфигурация веб-клиента.

---

### Итерация 5: Интеграция клиентов ✅

**Статус:** итерация **закрыта**. Оба клиента работают через **`/api/v1/`** (бот — [tasklist-backend](tasks/tasklist-backend.md), задача **07** ✅; веб — [tasklist-frontend](tasks/tasklist-frontend.md), итерация **4** ✅). Выполнен сквозной DoD: Telegram-бот и веб используют одно ядро; сценарий «студент фиксирует результат в боте → данные видны в веб-интерфейсе» подтверждён; клиенты не обращаются к LLM и БД напрямую.

**Цель:** подключить бот и веб к backend API — оба клиента работают через ядро, без собственной логики.

**Критерии завершения (DoD):**

- Telegram-бот переведён на вызовы backend API: диалог, фиксация результата, статус.
- Веб-клиент использует те же API-эндпоинты, что и бот — без дублирования логики.
- Сквозной сценарий «студент фиксирует результат в боте → данные видны в веб-интерфейсе» работает.
- Клиенты не обращаются к LLM и БД напрямую.

**Связь с tasklist:** [docs/tasks/tasklist-backend.md](tasks/tasklist-backend.md) (задача **07**) + [docs/tasks/tasklist-frontend.md](tasks/tasklist-frontend.md)

**Полезный результат:** платформа работает как единая система: один backend, два клиента.

**Артефакты:** [`bot/`](../bot/) (тонкий клиент), [`frontend/web/`](../frontend/web/).

---

### Итерация 6: Dev&Ops & Production ✅

**Уже сделано по [tasklist-devops](tasks/tasklist-devops.md):** [итерация 1](tasks/tasklist-devops.md#iteration-1-local-stack) (локальный compose, Dockerfile, `Makefile` / `tasks.ps1`, [docker-compose-local.md](tech/docker-compose-local.md)) и [итерация 2](tasks/tasklist-devops.md#iteration-2-ghcr) (GHCR, [`docker-compose.ghcr.yml`](../docker-compose.ghcr.yml), [`.github/workflows/ghcr.yml`](../.github/workflows/ghcr.yml) после зелёного CI). [итерация 3](tasks/tasklist-devops.md#iteration-3-timeweb-vps) (Timeweb, `twc`, [timeweb-vps.md](tech/timeweb-vps.md)). [итерация 4](tasks/tasklist-devops.md#iteration-4-server-setup) (bootstrap [`devops/vps`](../devops/vps/README.md), [vps-manual-ghcr-deploy.md](tech/vps-manual-ghcr-deploy.md), ручной `compose` на сервере). [итерация 5 (CD) в tasklist](tasks/tasklist-devops.md#iteration-5-cd-gha): job **Deploy to VPS** в [`.github/workflows/ghcr.yml`](../.github/workflows/ghcr.yml), секреты и сценарий — [docker-compose-ghcr.md § CD](tech/docker-compose-ghcr.md#cd-автодеплой-github-actions). [CI](../.github/workflows/ci.yml) — линт/сборка `frontend/web`, ruff, pytest. **Вне scope** devops-tasklist: Kubernetes, «полноценный» мониторинг, облачные бэкапы — см. [tasklist-devops, конец](tasks/tasklist-devops.md#вне-scope-граница-этого-tasklist).

**Цель:** контейнеризовать систему, настроить CI/CD и выполнить production-deploy.

⚡ **Параллельность:** при развитии проекта devops-задачи (CI, образы, CD) сочетаются с фиче-работой по [tasklist](tasks/) вне этого этапа.

**Критерии завершения (DoD):**

- Все компоненты (backend, бот, веб) контейнеризованы; `docker-compose` поднимает полный стек локально.
- CI проверяет линт и тесты при каждом PR.
- Production-deploy воспроизводим: одна команда/пайплайн доставляет обновление в прод.
- Секреты не в репозитории; конфиг из окружения валидируется при старте.
- Логирование: события уровня системы без текста переписки ([`vision.md §15`](vision.md)).

**Связь с tasklist:** [docs/tasks/tasklist-devops.md](tasks/tasklist-devops.md); см. также CI в [`.github/workflows/`](../.github/workflows/), команды в [`Makefile`](../Makefile), [`tasks.ps1`](../tasks.ps1) и [`README.md`](../README.md).

**Полезный результат:** система работает в продакшне; новый разработчик поднимает окружение по документации.

**Артефакты:** `Dockerfile` для каждого компонента, `docker-compose.yml`, CI-конфиг, `README.md` с инструкцией запуска.
