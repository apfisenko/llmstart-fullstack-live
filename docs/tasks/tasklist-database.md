# **Database Tasklist**

## **Обзор**

Внедрение полноценного слоя данных: от уточнения пользовательских сценариев и проектирования схемы до замены in-memory хранения на PostgreSQL с рабочей проверкой сквозных сценариев.

## **Легенда статусов**

- 📋 Planned — Запланирован
- 🚧 In Progress — В работе
- ✅ Done — Завершён

## Список задач


| Задача | Описание                                                                                 | Блок             | Статус | Документы                                                                                                                                                                           |
| ------ | ---------------------------------------------------------------------------------------- | ---------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01     | Сценарии студент/преподаватель и требования к данным (без глубокой техники)              | [1](#block-db-1) | ✅     | [план](impl/database/iteration-3-database/tasks/task-01-scenarios-data-reqs/plan.md) | [summary](impl/database/iteration-3-database/tasks/task-01-scenarios-data-reqs/summary.md)   |
| 02     | Схема данных: логика + физика, ER, ревью postgresql-table-design                         | [2](#block-db-2) | ✅     | [план](impl/database/iteration-3-database/tasks/task-02-schema-er-review/plan.md) | [summary](impl/database/iteration-3-database/tasks/task-02-schema-er-review/summary.md)         |
| 03     | ADR операций с БД + справка `db-tooling-guide.md` (Alembic, URL, make)                 | [3](#block-db-3) | ✅     | [план](impl/database/iteration-3-database/tasks/task-03-adr-db-tooling-guide/plan.md) | [summary](impl/database/iteration-3-database/tasks/task-03-adr-db-tooling-guide/summary.md) |
| 04     | Postgres в Docker, пересоздание окружения, миграции, сид из `progress-import`, make-цели | [4](#block-db-4) | ✅     | [план](impl/database/iteration-3-database/tasks/task-04-infra-seed-import/plan.md) | [summary](impl/database/iteration-3-database/tasks/task-04-infra-seed-import/summary.md)       |
| 05     | ORM, слой доступа к данным, интеграция backend под PostgreSQL, проверка API              | [5](#block-db-5) | ✅     | [план](impl/database/iteration-3-database/tasks/task-05-orm-repos-pg/plan.md) | [summary](impl/database/iteration-3-database/tasks/task-05-orm-repos-pg/summary.md)                 |


**Документы итерации:** [план итерации](impl/database/iteration-3-database/plan.md)  [summary итерации](impl/database/iteration-3-database/summary.md)

---



## Блок 1 — Задача 01: сценарии и требования к данным

### **Цель**

Зафиксировать, что видит и умеет студент и преподаватель — без технических деталей — и вывести из этого требования к данным, которые лягут в основу схемы БД и API.

### **Состав работ**

- Описать сценарии студента: просмотр текущего состояния собственного и лидерборд по выполнению домашек среди потока
- Описать сценарии преподавателя: просмотр участников, прогресс группы, активность за период в плане диалогов (вопросы студентов) и статистика (агрегатные функции по истории диалогов)
- Сохранить в `docs/tech/user-scenarios.md`
- Вывести требования к данным: какие сущности нужны, какие связи и как будут использоваться (без технических подробностей)
- Зафиксировать допущения учебного этапа: `модуль == урок`, `история == вопрос + ответ`
- Обновить `docs/vision.md` — раздел «Пользовательские сценарии» (конкретизировать под текущий этап)
- Самопроверка по критериям DoD

### **Критерии готовности (DoD)**

**Для агента:**

- Создан документ `docs/tech/user-scenarios.md` с полным описанием сценариев студента и преподавателя
- Из каждого сценария явно выведены необходимые данные и запросы
- Все допущения учебного этапа зафиксированы явно
- `docs/vision.md` раздел «Пользовательские сценарии» актуализирован

**Для пользователя:**

- Открыть `docs/tech/user-scenarios.md` — все сценарии читаются без технических деталей, каждый сценарий привязан к данным
- Открыть `docs/vision.md` — сценарии соответствуют тому, что планировалось на курсе

### **Артефакты**

- `docs/tech/user-scenarios.md` — пользовательские сценарии и требования к данным
- `docs/vision.md` — обновлённый раздел «Пользовательские сценарии»

### **Документы**

- 📋 ++[План итерации](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-0-user-scenarios/plan.md)++
- 📝 ++[Summary](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-0-user-scenarios/summary.md)++

---



## Блок 2 — Задача 02: проектирование схемы и ревью

### **Цель**

Упростить и актуализировать модель данных под учебный этап: зафиксировать допущения, обновить логическую и физическую модель, нарисовать физическую ER-диаграмму, провести ревью схемы.

### **Состав работ**

- Применить допущения: свернуть `Module` + `Lesson` → `Lesson` (единый уровень программы), упростить `Dialogue` + `Message` → хранить парами вопрос/ответ
- Актуализировать логическую модель в `docs/data-model.md` — описание сущностей и полей
- Нарисовать физическую ER-диаграмму (Mermaid): таблицы с типами колонок, PK/FK, индексы, constraints
- Ревью схемы через skill `postgresql-table-design`: проверить типы данных, индексы, naming, best practices
- Применить замечания по результатам ревью
- Самопроверка по критериям DoD

### **Критерии готовности (DoD)**

**Для агента:**

- `docs/data-model.md` описывает актуальный набор сущностей с применёнными допущениями
- Физическая ER-диаграмма содержит все таблицы, типы колонок (PostgreSQL), PK/FK, ключевые индексы
- Ревью по skill `postgresql-table-design` проведено, замечания задокументированы или применены

**Для пользователя:**

- Открыть `docs/data-model.md` — схема понятна, допущения явно отражены, ER-диаграмма рендерится в Mermaid
- Убедиться, что схема покрывает все сценарии из Итерации 0

### **Артефакты**

- `docs/data-model.md` — актуализированная логическая и физическая модель с ER-диаграммой

### **Документы**

- 📋 ++[План итерации](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-1-schema/plan.md)++
- 📝 ++[Summary](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-1-schema/summary.md)++

## Блок 3 — Задача 03: ADR и практическая справка по инструментам

### **Цель**

Зафиксировать выбор инструментов для работы с БД (ORM, миграции, драйвер) в ADR и подготовить краткую практическую справку о том, как они используются в нашем проекте.

### **Состав работ**

- Создать `docs/adr/adr-004-db-tooling.md`: зафиксировать выбор SQLAlchemy 2.x async + asyncpg + Alembic с обоснованием альтернатив; добавить в реестр `docs/adr/README.md`
- Создать `docs/tech/db-tooling-guide.md`: как инициализировать Alembic, создавать и применять миграции, структура `backend/` (`migrations/`, `app/domain/`, `app/infrastructure/`) — по `.cursor/rules/conventions.mdc`
- Описать соглашения проекта: именование таблиц, колонок, миграций; паттерн репозитория
- Добавить ссылку на справку из `docs/adr/adr-004-db-tooling.md`
- Самопроверка по критериям DoD

### **Критерии готовности (DoD)**

**Для агента:**

- `docs/adr/adr-004-db-tooling.md` зафиксированы практики репозитория и соглашения по схеме; выбор стека SQLAlchemy 2.x async + asyncpg + Alembic и разбор альтернатив (ORM, драйвер) — в `docs/adr/adr-002-backend-stack.md`
- `docs/tech/db-tooling-guide.md` описывает конкретные команды и структуру файлов в нашем проекте, не абстрактно
- Соглашения зафиксированы (snake_case, plurals, UUID vs serial, timestamptz)

**Для пользователя:**

- Открыть `docs/tech/db-tooling-guide.md` — по нему можно создать новую миграцию не гугля
- Открыть `docs/adr/adr-002-backend-stack.md` и `docs/adr/adr-004-db-tooling.md` — понятно, почему выбран стек и как им пользоваться в репозитории

### **Артефакты**

- `docs/adr/adr-004-db-tooling.md` — новый ADR
- `docs/tech/db-tooling-guide.md` — практическая справка

### **Документы**

- 📋 ++[План итерации](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-2-tooling/plan.md)++
- 📝 ++[Summary](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-2-tooling/summary.md)++

## Блок 4 — Задача 04: инфраструктура, миграции, сид, make

### **Цель**

Поднять PostgreSQL через Docker, настроить Alembic, создать и применить первую миграцию по схеме из Итерации 1, наполнить базу тестовыми данными из `progress-import.v1.json` тоже в виде миграции.

### **Состав работ**

- Добавить сервис `postgres` в `docker-compose.yml` (или создать файл); настроить volume, healthcheck
- Убедиться, что Alembic в `backend/`: `alembic.ini`, `backend/migrations/` (как в соглашениях проекта)
- Написать первую миграцию по схеме из Итерации 1 (все таблицы)
- Написать data-миграцию импорта из `data/progress-import.v1.json`
- Добавить `make`-команды: `db-up`, `db-down`, `db-reset`, `db-migrate`, `db-shell` (наполнение данных — ревизия `0003_seed_progress` после `0002_user_name`)
- Проверить: миграции применяются с нуля, ревизия сида `0003_seed_progress` отрабатывает без ошибок, данные видны в `db-shell`
- Обновить `docs/tech/db-tooling-guide.md` — добавить новые make-команды и другие документы Makefile
- Самопроверка по критериям DoD

### **Критерии готовности (DoD)**

**Для агента:**

- `make db-up` поднимает PostgreSQL, `make db-migrate` применяет все миграции без ошибок (`0001_initial`, `0002_user_name`, `0003_seed_progress`)
- Миграция `0003_seed_progress` импортирует данные из `progress-import.v1.json`: студенты, поток, прогресс
- `make db-reset` = down (с volume) + up + migrate — воспроизводимо с нуля
- `make db-shell` открывает psql; проверки: поток `M05 LLM Start Fullstack`, 13 студентов, 3 урока, 24 `progress_records` со статусом `completed` (в JSON импорта — `done`)

**Для пользователя:**

- Запустить: `make db-up && make db-migrate`
- В `make db-shell` выполнить проверочные `SELECT` из `docs/tech/db-tooling-guide.md`
- `make db-reset` завершается без ошибок и воспроизводит то же состояние

### **Артефакты**

- `docker-compose.yml` — сервис PostgreSQL
- `backend/alembic.ini`, `backend/migrations/` — Alembic (в т.ч. сид `0003_seed_progress`)
- `backend/app/domain/` — ORM-модели под схему (`target_metadata` для Alembic)
- `Makefile` — команды `db-`*
- `docs/tech/db-tooling-guide.md` — обновлённая справка с командами

### **Документы**

- 📋 ++[План итерации](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-3-infra/plan.md)++
- 📝 ++[Summary](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-3-infra/summary.md)++

## Блок 5 — Задача 05: ORM, доступ к данным, PostgreSQL в backend

### **Цель**

Реализовать ORM-модели и репозитории, заменить in-memory хранение на PostgreSQL в `backend/services/`, убедиться что сквозные сценарии работают.

### **Состав работ**

- Создать ORM-модели в `backend/app/domain/`: сущности по [`docs/data-model.md`](../data-model.md) — `User`, `Cohort`, `CohortMembership`, `Dialogue`, `DialogueTurn` (таблица `dialogue_turns`), `ProgressCheckpoint`, `ProgressRecord`
- Реализовать репозитории в `backend/app/infrastructure/`: по одному классу на сущность (или согласованный модуль), методы под сценарии из задачи 01
- Настроить async-сессию SQLAlchemy в `backend/app/infrastructure/`, dependency в `backend/app/api/deps.py`
- Переписать сервисы диалога: заменить `dict` в памяти на репозиторий диалогов / ходов (`dialogue_turns`)
- Переписать сервисы прогресса: заменить `dict` в памяти на репозиторий `ProgressRecord` / чекпоинтов
- Обновить `backend/config.py`: добавить `DATABASE_URL`, обновить `.env.example`
- Обновить тесты: использовать тестовую БД или моки репозиториев, `make backend-test` зелёный
- Провести sanitize + verify для каждого изменённого файла (`ruff check --fix`, `ruff format`, `mypy`)
- Обновить `docs/data-model.md` — сверить финальную схему с реализацией
- Самопроверка по критериям DoD

### **Критерии готовности (DoD)**

**Для агента:**

- `make db-up && make backend-dev` запускает backend, `/docs` открывается без ошибок
- Эндпоинты чата/прогресса по OpenAPI v1 сохраняют данные в БД; после перезапуска backend история и прогресс читаются из PostgreSQL, не из памяти процесса
- `make backend-test` — все тесты проходят
- `make backend-lint && make backend-typecheck` — без ошибок
- В `backend/services/` нет `dict`-переменных для хранения истории или прогресса

**Для пользователя:**

- `make db-reset && make backend-dev` — чистый старт
- Через `curl` или Swagger (`/docs`): отправить сообщение в чат, перезапустить backend, повторить запрос — история сохранилась
- Отметить прогресс, перезапустить backend, запросить прогресс — данные не потерялись
- `make backend-test` — зелёный вывод

### **Артефакты**

- `backend/app/domain/` — ORM-модели
- `backend/app/infrastructure/` — репозитории, async-сессия/движок
- `backend/app/api/deps.py` — зависимости FastAPI (сессия БД)
- `backend/services/dialogue.py` — переписан на БД
- `backend/services/progress.py` — переписан на БД
- `backend/config.py` — добавлен `DATABASE_URL`
- `.env.example` — обновлён
- `backend/tests/` — обновлённые тесты

### **Документы**

- 📋 ++[План итерации](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-4-orm/plan.md)++
- 📝 ++[Summary](https://github.com/apfisenko/llmstart-fullstack-aidd/blob/main/05-database/live/docs/tasks/impl/database/iteration-4-orm/summary.md)++

