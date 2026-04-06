# Backend Tasklist

## Обзор

Реализация **ядра** ([`vision.md`](../vision.md)): HTTP API для сценариев «вопрос ассистенту» и «фиксация выполненного домашнего задания / прогресса», интеграция с LLM **только в backend**, подготовка бота как тонкого клиента. Детализация по итерациям — в `docs/tasks/impl/backend/iteration-2-backend-api/` (см. [workflow](../../.cursor/rules/workflow.mdc)).

**Рекомендация по skills:** на этапах выбора стека и проектирования API уместно **рекомендовать** релевантные Agent Skills (например, `api-design-principles`, `fastapi-templates`, `python-testing-patterns`). Подбор выполнять через команду **`/find-skills`** в Cursor или по пути `.cursor/skills/find-skills/SKILL.md`.

## Связь с plan.md

| Задачи этого файла | Итерация [`plan.md`](../plan.md) |
|--------------------|----------------------------------|
| 01–06, 08 | Итерация 2 — Backend API |
| 07 | Итерация 5 — Интеграция клиентов (бот → backend); логически замыкает backend-контур |

## Легенда статусов

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён

---

## Список задач

| Задача | Описание | Блок | Статус | Документы |
|--------|----------|------|--------|-----------|
| 01 | Выбор backend-стека, ADR/соглашения, обновление `conventions.mdc` | [1](#block-backend-1) | ✅ Done | [план](impl/backend/iteration-2-backend-api/tasks/task-01-stack/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-01-stack/summary.md) |
| 02 | Проектирование API-контрактов (ассистент + фиксация ДЗ) | [1](#block-backend-1) | ✅ Done | [план](impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-02-contracts/summary.md) |
| 03 | Поднятие каркаса backend-сервиса (`pyproject.toml`, `uv`, структура `backend/app/`, health, конфиг) | [2](#block-backend-2) | ✅ Done | [план](impl/backend/iteration-2-backend-api/tasks/task-03-scaffold/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-03-scaffold/summary.md) |
| 04 | Базовые API-тесты сценариев, паритетных с текущим ботом | [2](#block-backend-2) | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-04-api-tests/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-04-api-tests/summary.md) |
| 05 | Реализация endpoint'ов, логики, персистентности (согласно `data-model.md`) | [3](#block-backend-3) | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-05-implementation/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-05-implementation/summary.md) |
| 06 | Документация backend: запуск, env, OpenAPI, команды | [4](#block-backend-4) | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-06-docs/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-06-docs/summary.md) |
| 07 | Рефакторинг бота: работа через backend API | [5](#block-backend-5) | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-07-bot-refactor/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-07-bot-refactor/summary.md) |
| 08 | Базовое качество: линт, тесты, CI, актуализация `Makefile` | [6](#block-backend-6) | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-08-quality/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-08-quality/summary.md) |

---

<a id="block-backend-1"></a>

## Блок 1 — Задачи 01–02: стек и контракты

### Задача 01: Выбор backend-стека и фиксация решений ✅

#### Цель

Зафиксировать стек backend (HTTP, работа с БД, миграции при необходимости), ключевое решение в ADR при необходимости; **обновить** `.cursor/rules/conventions.mdc` и согласованные фрагменты проектной документации под новый стек.

#### Состав работ

- [x] Оценить и выбрать HTTP-фреймворк и структуру приложения (например FastAPI; Python 3.9+, `uv`, `pyproject.toml`)
- [x] Определить подход к данным (async ORM, миграции) в соответствии с [`adr/adr-001-database.md`](../adr/adr-001-database.md) и [`data-model.md`](../data-model.md)
- [x] При значимом решении — ADR в `docs/adr/` (имя по принятам в [`adr/README.md`](../adr/README.md))
- [x] Обновить **`.cursor/rules/conventions.mdc`**: структура `backend/`, конфиг, логирование, тесты — без противоречий с [`vision.md`](../vision.md)
- [x] Актуализировать проектную документацию (по факту изменений): [`docs/vision.md`](../vision.md) (раздел про технологии и структуру репозитория), [`docs/plan.md`](../plan.md) (если меняются границы итерации или DoD), [`README.md`](../../README.md) (кратко, если меняется способ запуска)

#### Skills

Рекомендовать: **`/find-skills`** → при необходимости `fastapi-templates`, `api-design-principles`.

#### Definition of Done

**Агент (самопроверка):**

- Выбранный стек записан (ADR и/или `vision.md`); `conventions.mdc` отражает реальные пути и правила
- Нет противоречий с «ядро — backend», LLM только из backend, конфиг через `.env`

**Пользователь (ручная проверка):**

- Открыть `docs/adr/` + `conventions.mdc` — решения читаются без догадок
- Сверить с [`plan.md`](../plan.md) итерацию 2 — критерии по-прежнему достижимы

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-01-stack/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-01-stack/summary.md)

---

### Задача 02: Проектирование API-контрактов ✅

#### Цель

Зафиксировать HTTP-контракт для **двух базовых сценариев**: вопрос к ассистенту (диалог + LLM); фиксация выполненного домашнего задания / прогресса. Единый формат ошибок и коды ответов; основа для независимой работы бота и будущего веб-клиента.

#### Состав работ

- [x] Описать ресурсы и операции для диалога с ассистентом (запрос сообщения, ответ, при необходимости идентификация диалога/участника)
- [x] Описать ресурсы и операции для фиксации результата по [`data-model.md`](../data-model.md) (`ProgressCheckpoint` / `ProgressRecord` или согласованный MVP-срез)
- [x] Зафиксировать формат ошибок (тело, коды HTTP) и правило версионирования публичного API (заголовок или префикс `/v1/`)
- [x] Обновить [`docs/integrations.md`](../integrations.md) — как клиенты ходят в backend (без дублирования OpenAPI, но с указанием контрактной опоры)
- [x] При значимых изменениях домена — уточнить [`docs/data-model.md`](../data-model.md) (имена полей, обязательность)
- [x] Согласовать с [`docs/plan.md`](../plan.md) ожидания по итерации 2 (обзор потока / преподаватель — если входит в текущий этап, иначе явно отложено)

#### Skills

Рекомендовать: **`/find-skills`** → `api-design-principles`; при необходимости `fastapi-templates` для согласования структуры схем.

#### Definition of Done

**Агент (самопроверка):**

- Для обоих сценариев есть однозначные схемы запрос/ответ и коды ошибок
- Контракт согласован с сущностями из `data-model.md` или зафиксировано упрощение MVP

**Пользователь (ручная проверка):**

- Просмотреть черновик контракта (документ или OpenAPI-файл) — понятно, как бот вызовет API
- Проверить, что `integrations.md` не противоречит `vision.md` (клиенты не ходят в LLM/БД напрямую)

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-02-contracts/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-02-contracts/summary.md)
- Контракт: [`docs/api/openapi-v1.yaml`](../api/openapi-v1.yaml), сводка [`docs/tech/api-contracts.md`](../tech/api-contracts.md)

---

### Завершение блока 1 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | ADR/vision/conventions согласованы; контракт покрывает 2 сценария; ссылки на `data-model` не ломают домен |
| **Пользователь** | Читабельность решений в `docs/`; соответствие ожиданиям [`idea.md`](../idea.md) |
| **Команды** | Локальных сервисных команд на этом этапе может не быть; при добавлении — обновить `Makefile` (см. задачу 08) |
| **Где смотреть результат** | `docs/adr/`, `docs/vision.md`, `.cursor/rules/conventions.mdc`; контракт API — `docs/api/openapi-v1.yaml`, `docs/tech/api-contracts.md`, `docs/integrations.md` |

---

### Завершение блока 1 — результат проверки (2026-04-06)

| Критерий | Результат | Как проверено |
|----------|-----------|----------------|
| **Агент:** ADR / `vision` / `conventions` согласованы | OK | В [ADR README](../adr/README.md) ADR-001 и ADR-002; в [`vision.md`](../vision.md) §9 ссылка на ADR-002 и стек FastAPI; [`.cursor/rules/conventions.mdc`](../../.cursor/rules/conventions.mdc) — секция Backend совпадает с ADR-002 (FastAPI, SQLAlchemy async, Alembic, pydantic-settings). |
| **Агент:** контракт покрывает 2 сценария | OK | В [`openapi-v1.yaml`](../api/openapi-v1.yaml): диалог + LLM (`POST .../dialogues/messages`, `POST .../reset`); прогресс (`GET .../progress-checkpoints`, `PUT .../progress-records/...`); обзор потока (`GET .../summary`). Сводка в [`docs/tech/api-contracts.md`](../tech/api-contracts.md). |
| **Агент:** ссылки на `data-model` не ломают домен | OK | В [`data-model.md`](../data-model.md) у `ProgressRecord` зафиксированы enum API и ссылка на OpenAPI; сущности `Dialogue` / `ProgressCheckpoint` / `ProgressRecord` согласованы с планом задачи 02 и YAML. |
| **Пользователь:** читабельность `docs/` | OK* | Требуется визуальная вычитка человеком; структура документов и перекрёстные ссылки проверены. |
| **Пользователь:** соответствие [`idea.md`](../idea.md) | OK | Идея: сопровождение потока, бот как клиент, фиксация прогресса, обзор для преподавателя — отражены в контракте (единый API, прогресс, `summary`). |
| **Команды** | N/A | Новых целей в `Makefile` для блока 1 не требуется ([summary задачи 01](impl/backend/iteration-2-backend-api/tasks/task-01-stack/summary.md): README не менялся до задачи 06); команды — в задаче 08. |

\*Ручная вычитка — по чеклисту пользователя в DoD задач 01–02.

---

<a id="block-backend-2"></a>

## Блок 2 — Задачи 03–04: каркас и тесты

### Задача 03: Поднятие каркаса backend-сервиса ✅

#### Цель

Создать рабочий каркас `backend/`: структура `backend/app/`, `pyproject.toml` и `uv`, точка входа, конфигурация (fail-fast), `GET /health`, обновление [`.env.example`](../../.env.example) и при необходимости [`README.md`](../../README.md) — по [`vision.md`](../vision.md) и обновлённому `conventions.mdc`.

#### Состав работ

- [x] Создать структуру `backend/app/` (`api/`, `domain/` или эквивалент, `infrastructure/`, `services/` — по соглашению)
- [x] Настроить `pyproject.toml`, зависимости (`uv`), `ruff` для backend; точка входа приложения
- [x] Реализовать чтение конфигурации из окружения; **обновить** корневой и/или `backend/.env.example`
- [x] Реализовать `GET /health` (или согласованный путь); приложение слушает порт
- [x] Кратко обновить [`README.md`](../../README.md) при появлении новых команд запуска

#### Skills

Рекомендовать: **`/find-skills`** → `fastapi-templates`.

#### Definition of Done

**Агент (самопроверка):**

- Репозиторий собирается (`uv sync` или согласованная команда); структура соответствует `vision.md` и `conventions.mdc`
- Приложение стартует; при неполном `.env` — понятная ошибка
- Линт по backend проходит (или зафиксировано исключение в задаче 08)

**Пользователь (ручная проверка):**

- По `README` / `.env.example` запустить backend и открыть health в браузере или `curl`

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-03-scaffold/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-03-scaffold/summary.md)

---

### Задача 04: Базовые API-тесты (паритет с ботом) 📋

#### Цель

Автотесты на HTTP-слой для сценариев сообщений/действий, которые **уже есть** в текущем боте (что именно — зафиксировать в `plan.md` задачи по сравнению с `frontend/bot` или актуальным путём бота в репозитории). Моки LLM и при необходимости БД — чтобы тесты были стабильны.

#### Состав работ

- [ ] Инвентаризация текущих сценариев бота (handlers → ожидаемые вызовы backend)
- [ ] Написать тесты: happy path + ошибка валидации + (по возможности) сбой LLM без утечки текста в логи assertion'ом
- [ ] Подключить pytest в workspace, если ещё не подключён; целевые пути — `backend/tests/` (или согласованный каталог)

#### Skills

Рекомендовать: **`/find-skills`** → `python-testing-patterns`.

#### Definition of Done

**Агент (самопроверка):**

- `pytest` (или согласованная команда) завершается успешно в чистом окружении
- Тесты не зависят от реального OpenRouter/Telegram

**Пользователь (ручная проверка):**

- Запустить команду тестов из `README` или `Makefile` и увидеть зелёный прогон

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-04-api-tests/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-04-api-tests/summary.md)

---

### Завершение блока 2 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | Health отвечает; тесты зелёные; `.env.example` полный для локального старта backend |
| **Пользователь** | Запуск backend + один запуск тестов по документации |
| **Команды** | Добавить/актуализировать в `Makefile`: например `make backend-dev`, `make test-backend` (имена согласовать с [`README.md`](../../README.md)) |
| **Где смотреть результат** | `backend/`, вывод pytest, ответ `/health` |

---

<a id="block-backend-3"></a>

## Блок 3 — Задача 05: реализация

### Задача 05: Основные endpoint'ы и серверная логика 📋

#### Цель

Реализовать контракт задачи 02: диалог с LLM через backend, фиксация прогресса; персистентность по [`data-model.md`](../data-model.md) и [`adr/adr-001-database.md`](../adr/adr-001-database.md). Централизованная обработка сбоев LLM; логи без текста переписки ([`vision.md`](../vision.md) §15).

#### Состав работ

- [ ] Реализовать маршруты и сервисы диалога (LLM-клиент в `infrastructure/`, вызовы только отсюда)
- [ ] Реализовать маршруты фиксации прогресса / домашнего задания в терминах доменной модели
- [ ] Подключить PostgreSQL, миграции, ORM-модели — **или** зафиксировать в summary временную реализацию (in-memory) с явной связью с [`tasklist-database.md`](tasklist-database.md), если БД вынесена отдельной итерацией (не оставлять неявного долга)
- [ ] Обновить [`docs/data-model.md`](../data-model.md) при расхождении с фактической схемой
- [ ] Обновить [`docs/integrations.md`](../integrations.md) — детали LLM и БД на стороне backend

#### Актуализация документации (по необходимости)

- [`docs/vision.md`](../vision.md) — если меняются формулировки по LLM/данным
- [`docs/plan.md`](../plan.md) — если меняется охват итерации 2
- [`.env.example`](../../.env.example) — переменные БД и LLM для backend

#### Definition of Done

**Агент (самопроверка):**

- Оба сценария проходят интеграционно/тестами; данные не теряются при рестарте (если БД в scope)
- Нет прямого вызова LLM из клиентов; логи не содержат тела переписки в обычном режиме

**Пользователь (ручная проверка):**

- Через HTTP-клиент (curl/Bruno) или временный скрипт — отправить сообщение и зафиксировать прогресс; убедиться в ожидаемых ответах и кодах

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-05-implementation/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-05-implementation/summary.md)

---

### Завершение блока 3 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | Тесты из задачи 04 обновлены/зелёные; миграции накатываются командой из `Makefile` или `README` |
| **Пользователь** | Сценарии из `idea.md` воспроизводимы через API |
| **Команды** | `make test`, `make migrate` (или эквиваленты) — задокументированы |
| **Где смотреть результат** | OpenAPI/Swagger UI, ответы API, записи в БД (если включена) |

---

<a id="block-backend-4"></a>

## Блок 4 — Задача 06: документация backend

### Задача 06: Документирование backend 📋

#### Цель

Любой разработчик поднимает backend по инструкции: переменные окружения, запуск, OpenAPI, команды проверки.

#### Состав работ

- [ ] Обновить [`README.md`](../../README.md): установка, запуск backend, тесты, линт
- [ ] Дополнить [`.env.example`](../../.env.example) всеми переменными backend
- [ ] Обновить [`docs/integrations.md`](../integrations.md) — потоки данных и секреты
- [ ] Обновить [`docs/plan.md`](../plan.md) — статус итерации 2 при завершении
- [ ] Указать, где смотреть OpenAPI (встроенный `/docs` или `/openapi.json`)

#### Definition of Done

**Агент (самопроверка):**

- С нуля: клонирование → копия `.env` → запуск → health и `/docs` доступны
- Команды в `Makefile` и текст в `README` совпадают

**Пользователь (ручная проверка):**

- Пройти по `README` на чистой машине (или новом клоне) без «скрытых» шагов

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-06-docs/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-06-docs/summary.md)

---

### Завершение блока 4 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | Ссылки на OpenAPI и env полные; `plan.md` отражает факт |
| **Пользователь** | Открыть `README.md`, `.env.example`, Swagger |
| **Команды** | Все новые цели — в `Makefile` |
| **Где смотреть результат** | `README.md`, `docs/integrations.md`, UI документации API |

---

<a id="block-backend-5"></a>

## Блок 5 — Задача 07: клиент бота

### Задача 07: Рефакторинг бота под backend API 📋

> Связана с **итерацией 5** [`plan.md`](../plan.md); выполняется после готовности API и документации.

#### Цель

Бот — тонкий клиент: HTTP к backend; без прямого LLM и без долговременного хранения истории в памяти процесса бота (источник истины — backend/БД).

#### Состав работ

- [ ] Реализовать HTTP-клиент к backend в слое сервисов бота
- [ ] Перевести обработчики диалога и фиксации результата на API
- [ ] Удалить/сузить прямой LLM-клиент из бота
- [ ] Обновить [`.env.example`](../../.env.example) — URL backend, ключи клиента
- [ ] Обновить [`docs/integrations.md`](../integrations.md) и при необходимости [`README.md`](../../README.md)

#### Definition of Done

**Агент (самопроверка):**

- Нет импортов LLM в handlers; история не хранится в `dict` процесса бота в финальном виде
- Сквозной сценарий: сообщение в Telegram → запись/ответ через backend

**Пользователь (ручная проверка):**

- Запустить backend и бота; отправить сообщения и фиксацию — поведение как ожидается

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-07-bot-refactor/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-07-bot-refactor/summary.md)

---

### Завершение блока 5 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | Поиск по репо: нет прямого вызова OpenRouter из бота; тесты/линт зелёные |
| **Пользователь** | Ручной прогон в Telegram |
| **Команды** | `make run` / `make bot` / `make dev` — как зафиксировано в `Makefile` |
| **Где смотреть результат** | Логи backend (без текста переписки), ответы в Telegram |

---

<a id="block-backend-6"></a>

## Блок 6 — Задача 08: качество и инженерные практики

### Задача 08: Базовое качество и инженерные практики 📋

#### Цель

Единый стандарт качества: линт, тесты, при необходимости CI; новые команды локального запуска и обслуживания — в **`Makefile`**.

#### Состав работ

- [ ] Единые цели: `make lint`, `make test`, `make format` (или согласованные имена) — охватывают backend и при необходимости бот
- [ ] Подключить проверки в CI при наличии пайплайна; иначе зафиксировать в `README` обязательную локальную проверку перед PR
- [ ] Актуализировать [`docs/plan.md`](../plan.md) и [`docs/vision.md`](../vision.md) (§10–11) при изменении практик
- [ ] Ретроспектива контрактов: при необходимости вынести правила версионирования API в отдельный файл и ссылку из [`docs/integrations.md`](../integrations.md)

#### Definition of Done

**Агент (самопроверка):**

- `make lint` и `make test` завершаются с кодом 0 на чистом checkout (после `install`)
- Документация не расходится с командами

**Пользователь (ручная проверка):**

- Выполнить `make lint` и `make test` по инструкции; при необходимости проверить CI в PR

#### Документы задачи

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-08-quality/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-08-quality/summary.md)

---

### Завершение блока 6 — проверки

| Кто | Что проверить |
|-----|----------------|
| **Агент** | Все новые команды из задач 03–07 отражены в `Makefile`; дублирования нет |
| **Пользователь** | Один список команд в `README` |
| **Команды** | `make install`, `make lint`, `make test`, цели запуска backend/бота — согласованы |
| **Где смотреть результат** | `Makefile`, `README.md`, статус CI |

---

## Качество и инженерные практики (сквозные)

**Линт и формат.** `ruff` для Python-кода backend/бота — согласно обновлённому `conventions.mdc`.

**Тесты.** Минимум: happy path и ошибка валидации на ключевые endpoint'ы; мок LLM. См. skill `python-testing-patterns`.

**Наблюдаемость.** Stdout-логи; без текста пользовательских сообщений и ответов LLM в обычном режиме ([`vision.md`](../vision.md) §15).

**Контракты.** Breaking changes — только с явным версионированием API; фиксация в `integrations.md` или отдельном соглашении.

---

## Примечание о пересечении с database-итерацией

Если персистентность и миграции вынесены в отдельный [`tasklist-database.md`](tasklist-database.md), в summary задачи 05 явно указать временную стратегию (например, in-memory) и критерий переключения на PostgreSQL. Иначе — реализация БД остаётся частью задачи 05 в рамках итерации 2 [`plan.md`](../plan.md).
