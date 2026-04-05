# Backend Tasklist

## Обзор

Backend — ядро системы: бизнес-правила, LLM-интеграция, хранение данных и авторизация централизованы здесь. Бот и веб — тонкие клиенты без собственной логики; все продуктовые сценарии реализуются в backend и доступны любому новому клиенту без дублирования ([`vision.md §2`](../vision.md)).

## Связь с plan.md

| Задачи | Итерация [`plan.md`](../plan.md) |
|--------|-----------------------------------|
| 01–07, 09, 10 | Итерация 2 — Backend API |
| 08 | Итерация 5 — Интеграция клиентов |

## Легенда статусов

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён

---

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| 01 | Выбор стека и фиксация архитектурных решений | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-01-stack/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-01-stack/summary.md) |
| 02 | Scaffold backend-проекта | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-02-scaffold/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-02-scaffold/summary.md) |
| 03 | Проектирование API-контрактов | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-03-contracts/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-03-contracts/summary.md) |
| 04 | Реализация API диалога с LLM | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-04-dialogue/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-04-dialogue/summary.md) |
| 05 | Реализация API прогресса и потока | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-05-progress/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-05-progress/summary.md) |
| 06 | Подключение PostgreSQL и персистентность | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-06-database/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-06-database/summary.md) |
| 07 | Backend как единая точка входа для клиентов | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-07-entrypoint/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-07-entrypoint/summary.md) |
| 08 | Рефакторинг бота: переключение на backend API | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-08-bot-refactor/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-08-bot-refactor/summary.md) |
| 09 | Актуализация соглашений и документации | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-09-docs/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-09-docs/summary.md) |
| 10 | Сценарии локального запуска системы | 📋 Planned | [план](impl/backend/iteration-2-backend-api/tasks/task-10-local-run/plan.md) \| [summary](impl/backend/iteration-2-backend-api/tasks/task-10-local-run/summary.md) |

---

## Задача 01: Выбор стека и фиксация архитектурных решений 📋

### Цель

Зафиксировать технологические решения для backend: фреймворк, ORM/query builder, миграционный инструмент. Создать ADR, если решение значимо для архитектуры системы в целом.

### Состав работ

- [ ] Оценить и выбрать HTTP-фреймворк (FastAPI или аналог — Python 3.9+, `uv`)
- [ ] Определить инструмент работы с БД (SQLAlchemy async / иной подход)
- [ ] Определить инструмент миграций (Alembic или аналог)
- [ ] Зафиксировать решения в ADR (при необходимости) и обновить `vision.md §9`

### Артефакты

- `docs/adr/adr-00N-backend-stack.md` — ADR по стеку (если создаётся)
- Обновлённый раздел `vision.md §9` — технологии

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-01-stack/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-01-stack/summary.md)

---

## Задача 02: Scaffold backend-проекта 📋

### Цель

Создать рабочий каркас `backend/` с правильной структурой, конфигурацией и health endpoint. Backend стартует, читает `.env`, падает с понятной ошибкой при неполной конфигурации.

### Состав работ

- [ ] Создать структуру `backend/app/` (api/, domain/, infrastructure/, services/)
- [ ] Настроить `pyproject.toml`, `uv`, `ruff` для backend
- [ ] Реализовать `config.py` с fail-fast при отсутствии обязательных переменных
- [ ] Добавить `.env.example` для backend
- [ ] Реализовать `GET /health` — минимальный health endpoint
- [ ] Убедиться, что линт и базовый запуск проходят

### Артефакты

- `backend/app/` — каркас проекта
- `backend/pyproject.toml` — зависимости и конфигурация инструментов
- `backend/.env.example` — шаблон переменных окружения

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-02-scaffold/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-02-scaffold/summary.md)

---

## Задача 03: Проектирование API-контрактов 📋

### Цель

Зафиксировать схемы запросов и ответов для всех продуктовых endpoint'ов до начала реализации. Контракт — основа для независимой работы над ботом и веб-клиентом.

### Состав работ

- [ ] Описать схемы для диалога: запрос сообщения, ответ ассистента, история
- [ ] Описать схемы для прогресса: фиксация результата, статус этапа, список этапов
- [ ] Описать схему агрегированного среза по потоку (для преподавателя)
- [ ] Определить единый формат ошибок и коды ответов
- [ ] Убедиться, что OpenAPI-схема генерируется корректно (Swagger UI / ReDoc)

### Артефакты

- Pydantic-схемы в `backend/app/api/` — модели запросов/ответов
- OpenAPI-документация доступна при запуске backend

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-03-contracts/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-03-contracts/summary.md)

---

## Задача 04: Реализация API диалога с LLM 📋

### Цель

Реализовать endpoint диалога: backend принимает сообщение, обращается к LLM-провайдеру и возвращает ответ. Сбои LLM обрабатываются централизованно; текст переписки не попадает в логи.

### Состав работ

- [ ] Реализовать `POST /dialogue/message` по зафиксированному контракту
- [ ] Реализовать LLM-клиент в `backend/app/infrastructure/` (OpenAI-совместимый, OpenRouter)
- [ ] Централизованная обработка сбоев провайдера: понятный ответ клиенту + логирование без текста
- [ ] Сохранять `DialogueMessage` в БД (после подключения — задача 06)
- [ ] Логировать: `chat_id`, длину запроса/ответа, ошибки — без текста переписки

### Артефакты

- `backend/app/api/dialogue.py` — маршруты диалога
- `backend/app/infrastructure/llm.py` — LLM-клиент
- `backend/app/services/dialogue_service.py` — сценарий диалога

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-04-dialogue/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-04-dialogue/summary.md)

---

## Задача 05: Реализация API прогресса и потока 📋

### Цель

Реализовать endpoint'ы фиксации прогресса студента и агрегированного среза по потоку для преподавателя. Сущности `ProgressCheckpoint` и `ProgressRecord` доступны через API.

### Состав работ

- [ ] Реализовать `POST /progress` — фиксация результата студентом
- [ ] Реализовать `GET /progress/{membership_id}` — статус прогресса участника
- [ ] Реализовать `GET /cohort/{cohort_id}/overview` — срез активности группы
- [ ] Покрыть endpoint'ы базовой валидацией входных данных

### Артефакты

- `backend/app/api/progress.py` — маршруты прогресса
- `backend/app/api/cohort.py` — маршруты потока
- `backend/app/services/progress_service.py` — сценарии прогресса

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-05-progress/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-05-progress/summary.md)

---

## Задача 06: Подключение PostgreSQL и персистентность 📋

### Цель

Подключить PostgreSQL к backend; описать ORM-модели для всех доменных сущностей из `data-model.md`; запустить базовые миграции. Данные переживают рестарт процесса.

### Состав работ

- [ ] Подключить PostgreSQL (async-драйвер); валидировать соединение при старте — fail fast
- [ ] Реализовать ORM-модели: `User`, `Cohort`, `CohortMembership`, `Dialogue`, `DialogueMessage`, `ProgressCheckpoint`, `ProgressRecord`
- [ ] Настроить инструмент миграций; создать и накатить начальную миграцию
- [ ] Переключить задачи 04 и 05 на персистентное хранение вместо памяти

### Артефакты

- `backend/app/infrastructure/database.py` — подключение и сессии
- `backend/app/domain/` — ORM-модели сущностей
- `backend/migrations/` — миграции (Alembic или аналог)

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-06-database/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-06-database/summary.md)

---

## Задача 07: Backend как единая точка входа для клиентов 📋

### Цель

Обеспечить минимальную идентификацию запросов от клиентов (бот, веб), чтобы backend мог различать и авторизовывать источники запросов. Клиенты готовы к интеграции без доработок ядра.

### Состав работ

- [ ] Определить и реализовать схему идентификации клиента (API-key / telegram user_id / сессия)
- [ ] Обеспечить передачу идентификатора пользователя в продуктовые endpoint'ы
- [ ] Проверить, что health endpoint и все продуктовые маршруты доступны из внешнего запроса
- [ ] Описать схему идентификации в API-контракте (задача 03 → обновление)

### Артефакты

- `backend/app/api/dependencies.py` — зависимости авторизации/идентификации
- Обновлённые схемы запросов с полем идентификации клиента

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-07-entrypoint/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-07-entrypoint/summary.md)

---

## Задача 08: Рефакторинг бота — переключение на backend API 📋

> Задача относится к **Итерации 5** [`plan.md`](../plan.md). Ведётся в этом tasklist как логическое завершение backend-контура.

### Цель

Бот становится тонким клиентом: убрать прямой вызов LLM и хранение состояния из `frontend/bot/`, заменить на HTTP-запросы к backend API.

### Состав работ

- [ ] Убрать `LLMService` / прямые вызовы LLM из `frontend/bot/`
- [ ] Реализовать HTTP-клиент к backend API в `frontend/bot/services/`
- [ ] Переключить handlers диалога, фиксации результата и статуса на вызовы backend
- [ ] Убедиться, что бот не хранит историю в памяти процесса
- [ ] Проверить сквозной сценарий: студент пишет боту → данные видны через API

### Артефакты

- `frontend/bot/services/backend_client.py` — HTTP-клиент к backend
- Удалён / упрощён `frontend/bot/services/llm_service.py`

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-08-bot-refactor/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-08-bot-refactor/summary.md)

---

## Задача 09: Актуализация соглашений и документации 📋

### Цель

Привести проектную документацию в соответствие с реализованным backend: форматы запросов, коды ошибок, правила версионирования API.

### Состав работ

- [ ] Обновить `vision.md` — технологии (§9), архитектурные решения (§6), если изменились
- [ ] Обновить `data-model.md` — уточнить поля и связи по факту реализованных ORM-моделей
- [ ] Обновить `integrations.md` — добавить детали по PostgreSQL и LLM-клиенту backend
- [ ] Зафиксировать в `integrations.md` или отдельном файле: форматы запросов, коды ошибок, правило версионирования (breaking change → новая версия API)

### Артефакты

- Обновлённые `docs/vision.md`, `docs/data-model.md`, `docs/integrations.md`
- Опционально: `docs/api-conventions.md` — форматы и правила изменений контрактов

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-09-docs/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-09-docs/summary.md)

---

## Задача 10: Сценарии локального запуска системы 📋

### Цель

Любой разработчик поднимает полный стек локально по инструкции. Все ключевые операции доступны через `make`.

### Состав работ

- [ ] Создать / обновить `Makefile` с командами: `make dev`, `make test`, `make lint`, `make migrate`
- [ ] Создать `docker-compose.yml` для локального стека (backend + PostgreSQL)
- [ ] Описать инструкцию запуска в `README.md` (клонирование → `.env` → `make dev`)
- [ ] Убедиться, что `make test` и `make lint` завершаются с кодом 0 на чистом checkout

### Артефакты

- `Makefile` — команды разработки и проверки
- `docker-compose.yml` — локальный стек
- `README.md` — инструкция запуска

### Документы

- 📋 [План](impl/backend/iteration-2-backend-api/tasks/task-10-local-run/plan.md)
- 📝 [Summary](impl/backend/iteration-2-backend-api/tasks/task-10-local-run/summary.md)

---

## Качество и инженерные практики

**Линт и формат.** `ruff check` + `ruff format` — обязательны локально и в CI. Нарушение блокирует merge.

**Тесты.** Минимальный smoke-тест на каждый продуктовый endpoint (happy path + ошибка валидации). Отдельный тест: сбой LLM-провайдера → понятный ответ клиенту, не 500 без сообщения.

**Наблюдаемость.** Логирование в stdout, уровень из конфигурации. Логируются: старт/стоп, технические события запросов (без текста переписки), ошибки зависимостей. Идентификаторы пользователей — обезличенно.

**Правила изменений контрактов.** Breaking change в API → версия (`/v2/...` или заголовок версии). Изменения схемы БД — только через миграцию, не вручную. Схема обратной совместимости фиксируется в `integrations.md` или `api-conventions.md`.
