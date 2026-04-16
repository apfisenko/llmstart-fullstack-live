# Frontend Tasklist

## Обзор

Реализация **веб-клиента** платформы (`[vision.md](../vision.md)` §1–2): единое приложение с ролями студента и преподавателя, вызовы **только** в HTTP API ядра (`/api/v1/`), без дублирования бизнес-логики и без прямого доступа к LLM и БД.

**Стек:** Next.js (App Router), React, TypeScript, shadcn/ui, Tailwind CSS, **pnpm**.

**Сводные требования к веб-клиенту (единый документ):** `[docs/tech/frontend-requirements.md](../tech/frontend-requirements.md)`.

Детализация по итерации — в `docs/tasks/impl/frontend/iteration-4-frontend/` (см. [workflow](../../.cursor/rules/workflow.mdc)).

**Рекомендация по skills:** `/find-skills` или `[.cursor/skills/find-skills/SKILL.md](../../.cursor/skills/find-skills/SKILL.md)`; для UI — `[.cursor/skills/shadcn-ui/SKILL.md](../../.cursor/skills/shadcn-ui/SKILL.md)`; для Next/Vercel — `[.cursor/skills/vercel-react-best-practice/SKILL.md](../../.cursor/skills/vercel-react-best-practice/SKILL.md)`, `[.cursor/skills/nextjs-app-router-patterns/SKILL.md](../../.cursor/skills/nextjs-app-router-patterns/SKILL.md)`; для API — `[.cursor/skills/api-design-principles/SKILL.md](../../.cursor/skills/api-design-principles/SKILL.md)`; для регрессий и окружения — `[.cursor/skills/sharp-edges/SKILL.md](../../.cursor/skills/sharp-edges/SKILL.md)`.

## Связь с plan.md


| Задачи этого файла | Итерация `[plan.md](../plan.md)`                                                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01–08, **11**      | Итерация 4 — Реализация Frontend; **11** закрывает пробел зоны C (кабинет студента), не входивший в исходную нумерацию 04–07                                                    |
| 09–10              | Логически после MVP веб-UI: пересечение с итерациями **5** (интеграция клиентов), **6** (инфраструктура) и отдельными ADR; при планировании спринта уточнить привязку к roadmap |


## Легенда статусов

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён
- ⛔ Cancelled — отменена (не выполняется)

## Документы итерации

- План итерации: [plan.md](impl/frontend/iteration-4-frontend/plan.md) (создать при старте)
- Summary итерации: [summary.md](impl/frontend/iteration-4-frontend/summary.md) (создать при закрытии)

## Окружение команд

- **PowerShell** на Windows — основной способ запуска `make`, `pnpm`, `uv` на хосте.
- **Docker / Postgres:** при необходимости использовать **WSL** или переопределение `DOCKER_COMPOSE` (см. комментарии в [Makefile](../../Makefile) и `[docs/tech/db-tooling-guide.md](../tech/db-tooling-guide.md)`).



## Визуальные образцы UI (макеты)


| Экран                                     | Файл                                               | Назначение                                                                                                 |
| ----------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Панель преподавателя (дашборд)            | `[docs/ui/dashboard.png](../ui/dashboard.png)`     | Ориентир по компоновке: KPI, график диалогов с AI, лента сдач, матрица прогресса, тёмная тема и акценты    |
| Лидерборд (таблица и переключатель видов) | `[docs/ui/leaderboard.png](../ui/leaderboard.png)` | Ориентир по таблице рейтинга, прогресс-барам, иконкам уроков, топ-3 и переключателю «Таблица / Координаты» |


В задачах **01**, **04** и **05** макеты использовать как целевой образ вёрстки вместе с `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)`. Якорь для ссылок из текста: `#ui-mockups`.

---

## Список задач


| Задача | Описание                                                                                  | Блок                   | Статус | Документы                                                                                                                                                                     |
| ------ | ----------------------------------------------------------------------------------------- | ---------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01     | Требования к UI (4 зоны), стиль, вход по Telegram username, проектирование API под экраны | [1](#block-frontend-1) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/summary.md)   |
| 02     | Backend: данные, новые endpoint'ы, миграции mock + преподаватель @akozhin, контракты      | [1](#block-frontend-1) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-02-backend-api-seed/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-02-backend-api-seed/summary.md)   |
| 03     | Каркас Next.js + shadcn + тема + вход + layout + чат-виджет + Makefile/README             | [2](#block-frontend-2) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-03-next-scaffold/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-03-next-scaffold/summary.md)         |
| 04     | Панель преподавателя (KPI, график, вопросы, сдачи, матрица)                               | [3](#block-frontend-3) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-04-teacher-dashboard/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-04-teacher-dashboard/summary.md)   |
| 05     | Лидерборд: таблица / scatter plot                                                         | [3](#block-frontend-3) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-05-leaderboard/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-05-leaderboard/summary.md)             |
| 06     | Глобальный чат (плавающая панель, история)                                                | [3](#block-frontend-3) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-06-chat-floating/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-06-chat-floating/summary.md)         |
| 07     | Чат в основной области (меню «Чат», история)                                              | [3](#block-frontend-3) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-07-chat-main-route/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-07-chat-main-route/summary.md)     |
| 08     | Ревью качества frontend (best practices, критические исправления)                         | [4](#block-frontend-4) | ✅      | [план](impl/frontend/iteration-4-frontend/tasks/task-08-frontend-quality/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-08-frontend-quality/summary.md)   |
| 09     | Голосовой режим чата (веб + Telegram-бот)                                                 | [5](#block-frontend-5) | ⛔     | [план](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/summary.md)               |
| 10     | Ответы на вопросы по данным БД (Text-to-SQL): веб + бот через backend; после плана — **не в работе** (усложнение), бэклог | [5](#block-frontend-5) | ⛔     | [план](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/summary.md)             |
| 11     | Кабинет студента (зона C): прогресс, список уроков, сдача через API                                                       | [3](#block-frontend-3) | ✅     | [план](impl/frontend/iteration-4-frontend/tasks/task-11-student-cabinet/plan.md) | [summary](impl/frontend/iteration-4-frontend/tasks/task-11-student-cabinet/summary.md)       |


---



## Блок 1 — Задачи 01–02: требования, контракты и API ядра

### Задача 01: Требования к UI и API-контракты для frontend ✅

#### Цель

Зафиксировать краткие функциональные требования по зонам интерфейса, общий визуальный стиль и модель входа; спроектировать HTTP-контракты под все экраны веб-клиента.

#### Состав работ

- Сформировать краткие требования к **четырём зонам** на основе `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)` и **визуальных макетов** (см. [визуальные образцы UI](#ui-mockups)): зона A — `[docs/ui/dashboard.png](../ui/dashboard.png)`; зона B — `[docs/ui/leaderboard.png](../ui/leaderboard.png)`.
  - **Зона A — панель преподавателя:** 4 KPI с дельтой к прошлой неделе; линейный график активности (вопросы к ассистенту) по дням за **14 дней** (и/или предустановки периодов); лента вопросов (кто, когда, вопрос + ответ; пагинация/поиск по согласованию с API); лента сдач (клик — отчёт и ссылки); матрица прогресса (студенты × уроки/чекпоинты, дата сдачи при наведении).
  - **Зона B — лидерборд:** переключатель «таблица / scatter plot»; в таблице — место, прогресс-бар, иконки по урокам, топ-3 с медалями; карта — оси и подсказка по точке (имя, цифры).
  - **Зона C — личный кабинет студента** (экран 3 в UI-доке): приветствие, прогресс, список уроков, форма сдачи — согласовать с roadmap итерации 4 (`[plan.md](../plan.md)` §итерация 4).
  - **Зона D — глобальный чат:** плавающая кнопка на всех экранах; панель поверх контента; история + ввод; стиль «терминал / IDE».
- Зафиксировать общий стиль UI: **тёмная тема**, dev-эстетика в духе [tbench.ai](https://www.tbench.ai/).
- Зафиксировать **вход без сложной авторизации:** идентификация через ввод **Telegram username** (и согласование с backend: токен, membership, заглушки MVP — явно описать).
- Спроектировать ресурсы и операции API для зон A–D и навигации (списки, фильтры, агрегаты); согласовать с `[docs/data-model.md](../data-model.md)` и текущим `[docs/tech/api-contracts.md](../tech/api-contracts.md)`.
- Актуализировать проектную документацию: `[docs/tech/api-contracts.md](../tech/api-contracts.md)`, `[docs/api/openapi-v1.yaml](../api/openapi-v1.yaml)`; при изменении домена — `[docs/data-model.md](../data-model.md)`; при изменении потока данных между клиентами — `[docs/integrations.md](../integrations.md)`.

#### Skills

`api-design-principles`; при необходимости `find-skills`.

#### Критерии готовности (DoD)

**Для агента:**

- Есть структурированное описание зон A–D и входа; нет противоречий с `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)` и `[docs/vision.md](../vision.md)`.
- Черновик контрактов покрывает данные для дашборда, лидерборда, кабинета студента и чата; имена полей и роли согласованы с доменом.
- Обновлены `api-contracts.md` и OpenAPI (или зафиксировано, что меняется только в задаче 02, с явной ссылкой в `plan.md` задачи).

**Для пользователя:**

- Открыть `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)`, макеты `[docs/ui/dashboard.png](../ui/dashboard.png)` и `[docs/ui/leaderboard.png](../ui/leaderboard.png)`, текст задачи 01 — сценарии и визуальный уровень совпадают с ожиданиями.
- Открыть `[docs/tech/api-contracts.md](../tech/api-contracts.md)` / OpenAPI — понятно, какие вызовы сделает веб для каждого экрана.

#### Артефакты

- Обновлённые: `[docs/tech/api-contracts.md](../tech/api-contracts.md)`, `[docs/api/openapi-v1.yaml](../api/openapi-v1.yaml)` (после согласования).

#### Документы задачи

- 📋 [План](impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/plan.md)
- 📝 [Summary](impl/frontend/iteration-4-frontend/tasks/task-01-ui-api-contracts/summary.md)

---

### Задача 02: Реализация API для frontend (backend) ✅

#### Цель

Обеспечить данными и endpoint'ами всё, что нужно для отрисовки экранов из задач 01 и 04–07; наполнить БД осмысленными mock-данными и учётной записью преподавателя.

#### Состав работ

- Сверить `[docs/data-model.md](../data-model.md)` и фактическую схему БД: достаточно ли сущностей для KPI, графика, лент, матрицы, лидерборда, чата; сформулировать **требования к данным** (поля, агрегаты, индексы) при пробелах.
- Реализовать в `backend/` новые маршруты `/api/v1/...`, репозитории/сервисы по необходимости; миграции Alembic при расширении схемы.
- Добавить миграцию (или сид) с **mock-данными** для демонстрации UI (когорта, участники, ходы диалогов, прогресс).
- Добавить в миграцию/сид пользователя **преподавателя**: Telegram **@akozhin**, `telegram_user_id` **162684825** (и привязку к потоку — по согласованной модели).
- Самопроверка по skill `**api-design-principles`** (ресурсы, коды ошибок, версионирование `/api/v1/`).
- Обновить `[docs/tech/api-contracts.md](../tech/api-contracts.md)` и `[docs/api/openapi-v1.yaml](../api/openapi-v1.yaml)`; при изменении схемы — `[docs/data-model.md](../data-model.md)`.

#### Skills

`api-design-principles`, `postgresql-table-design` (при изменении таблиц), `python-testing-patterns` (тесты новых endpoint'ов).

#### Критерии готовности (DoD)

**Для агента:**

- Новые endpoint'ы покрывают контракт задачи 01; pytest/httpx или согласованный минимум тестов для критичных путей.
- Миграции накатываются на чистую БД; mock-данные и преподаватель @akozhin присутствуют после миграции/сида.
- Документация API синхронизирована с кодом.

**Для пользователя:**

- В PowerShell: поднять БД (при необходимости через WSL / `DOCKER_COMPOSE`, см. [Makefile](../../Makefile)), выполнить `make db-migrate` / цели из `[docs/tech/db-tooling-guide.md](../tech/db-tooling-guide.md)`, запустить `make backend-dev`, открыть `/docs` или OpenAPI — новые пути видны.
- Проверить в БД или через API наличие пользователя с `telegram_user_id = 162684825`.

#### Артефакты

- `backend/app/api/`, `backend/app/services/`, `backend/migrations/`, тесты в `backend/tests/`.

#### Документы задачи

- ✅ [План](impl/frontend/iteration-4-frontend/tasks/task-02-backend-api-seed/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-02-backend-api-seed/summary.md)

---

### Завершение блока 1 — проверки


| Кто              | Что проверить                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Агент**        | Контракты задачи 01 реализованы в задаче 02; нет расхождения OpenAPI ↔ код; mock-данные достаточны для UI                            |
| **Пользователь** | Читабельность `docs/tech/api-contracts.md`; сценарии из UI-дока достижимы через API                                                  |
| **Команды**      | Новые сервисные команды (например сид frontend-demo) — добавить в [Makefile](../../Makefile) и кратко в [README.md](../../README.md) |


---



## Блок 2 — Задача 03: каркас frontend-проекта

### Задача 03: Каркас Next.js + тема + вход + layout ✅

#### Цель

Инициализировать единый веб-проект (целевая раскладка из `[plan.md](../plan.md)`: `frontend/web/`), настроить UI-стек и навигацию, глобальный чат-виджет и автоматизацию запуска.

#### Состав работ

- Инициализировать проект: **Next.js (App Router)** + **TypeScript** + **Tailwind** + **pnpm**; подключить **shadcn/ui** по skill `shadcn-ui`.
- Настроить **тёмную тему** и визуальную базу в духе [tbench.ai](https://www.tbench.ai/) (типографика, фон, акценты, компоненты).
- Реализовать **вход по Telegram username** (MVP): сохранение контекста пользователя на клиенте, отображение информации о пользователе и **кнопка выхода**; вызовы backend согласно задаче 02.
- Базовый **layout**: навигация по основным экранам (дашборд преподавателя, лидерборд, кабинет студента, пункт «Чат»); **глобальный чат-виджет** (плавающая кнопка — каркас, полная логика в задаче 06).
- Автоматизация: цели в [Makefile](../../Makefile) — например `frontend-install`, `frontend-dev`, `frontend-lint`, `frontend-build` (уточнить имена в `plan.md` задачи); кратко обновить [README.md](../../README.md).
- Актуализировать при необходимости: `[docs/vision.md](../vision.md)` (пути артефактов), `[docs/integrations.md](../integrations.md)` (как веб ходит в backend).

#### Skills

`shadcn-ui`, `vercel-react-best-practice`, `nextjs-app-router-patterns`, `sharp-edges`.

#### Критерии готовности (DoD)

**Для агента:**

- Репозиторий содержит каталог `frontend/web/` (или согласованный путь) с рабочим `pnpm dev`; shadcn и Tailwind подключены без ошибок сборки.
- Layout и навигация открывают заглушки маршрутов; виджет чата присутствует как UI-элемент.
- В Makefile есть цели для установки и запуска фронта; README не противоречит командам.

**Для пользователя:**

- В PowerShell: `pnpm install` / `make frontend-dev` (или эквивалент из README) — приложение открывается в браузере, тема тёмная, навигация кликабельна.

#### Артефакты

- `frontend/web/` (`package.json`, `app/`, компоненты shadcn), обновлённые `Makefile`, `README.md`.

#### Документы задачи

- 📋 [План](impl/frontend/iteration-4-frontend/tasks/task-03-next-scaffold/plan.md)
- 📝 [Summary](impl/frontend/iteration-4-frontend/tasks/task-03-next-scaffold/summary.md)

---



## Блок 3 — Задачи 04–07 и 11: экраны, кабинет студента и чат

### Задача 04: Панель преподавателя ✅

#### Цель

Страница дашборда преподавателя с KPI, графиком, таблицей вопросов, лентой сдач и матрицей прогресса.

#### Визуальный образец

Макет: `[docs/ui/dashboard.png](../ui/dashboard.png)` (сверка компоновки, иерархии блоков, тёмной темы и акцентов с реализацией).

#### Состав работ

- Сверстать и связать с API по макету `[docs/ui/dashboard.png](../ui/dashboard.png)`; отклонения — только осознанные (зафиксировать в summary задачи).
- 4 KPI-карточки с дельтой; данные с backend.
- Линейный график активности за 14 дней (и обработка состояний загрузки/ошибки).
- Таблица/лента вопросов (кто, когда, вопрос + ответ); пагинация согласно API.
- Лента последних сдач с переходом к отчёту и ссылкам.
- Матрица студенты × уроки с подсказкой даты при наведении.
- При необходимости обновить `[docs/tech/api-contracts.md](../tech/api-contracts.md)` (уточнения полей ответа).

#### Skills

`shadcn-ui`, `vercel-react-best-practice`, `nextjs-app-router-patterns`.

#### Критерии готовности (DoD)

**Для агента:**

- Страница использует только публичный API; состояния loading/empty/error обработаны; типы ответов согласованы с OpenAPI.

**Для пользователя:**

- Запустить backend с mock-данными и `pnpm dev` в `frontend/web/`; открыть маршрут панели преподавателя — все блоки заполнены данными с сервера; визуально сопоставить с `[docs/ui/dashboard.png](../ui/dashboard.png)`.

#### Документы задачи

- ✅ [План](impl/frontend/iteration-4-frontend/tasks/task-04-teacher-dashboard/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-04-teacher-dashboard/summary.md)

---

### Задача 05: Лидерборд ✅

#### Цель

Страница лидерборда с переключателем «Таблица / Карта» и визуализацией топ-3.

#### Визуальный образец

Макет табличного вида и шапки с переключателем: `[docs/ui/leaderboard.png](../ui/leaderboard.png)` (режим «Координаты» / scatter — по тому же стилю, если в макете не показан).

#### Состав работ

- Сверстать табличный режим и переключатель видов по макету `[docs/ui/leaderboard.png](../ui/leaderboard.png)`; отклонения — зафиксировать в summary.
- Переключатель видов: таблица и scatter plot.
- Таблица: место, прогресс-бар, иконки по урокам, медали для топ-3.
- Scatter: оси, точки, tooltip с именем и метриками.
- Интеграция с endpoint'ами задачи 02.

#### Skills

`shadcn-ui`, `vercel-react-best-practice`.

#### Критерии готовности (DoD)

**Для агента:**

- Оба режима отображают согласованные с API данные; переключение без потери контекста потока.

**Для пользователя:**

- Открыть страницу лидерборда, переключить «Таблица / Карта», проверить топ-3 и подсказки на карте; табличный вид сопоставить с `[docs/ui/leaderboard.png](../ui/leaderboard.png)`.

#### Документы задачи

- ✅ [План](impl/frontend/iteration-4-frontend/tasks/task-05-leaderboard/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-05-leaderboard/summary.md)

---

### Задача 06: Глобальный чат (плавающая панель) ✅

#### Цель

Реализовать чат с ассистентом в виде **плавающей панели** на всех экранах: история и отправка сообщений через backend.

#### Состав работ

- Панель по клику на FAB; закрытие без потери маршрута; история прокручиваема.
- Отправка сообщений и отображение ответов (streaming — по согласованию и возможностям API).
- Стиль сообщений как в `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)` (терминальный / IDE).
- Не логировать и не выводить в UI лишние персональные данные; соблюдать правила логирования проекта.

#### Skills

`nextjs-app-router-patterns`, `sharp-edges` (границы client/server, кэш).

#### Критерии готовности (DoD)

**Для агента:**

- Виджет подключён в корневом layout; используется тот же диалоговый API, что и для маршрута «Чат», либо задокументировано разделение (например `dialogue_id` в session storage).

**Для пользователя:**

- С любой страницы открыть чат, отправить сообщение, увидеть ответ; обновить страницу — поведение истории согласовано с контрактом.

#### Документы задачи

- ✅ [План](impl/frontend/iteration-4-frontend/tasks/task-06-chat-floating/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-06-chat-floating/summary.md)

---

### Задача 07: Чат в основной области (меню «Чат») ✅

#### Цель

Отдельная страница «Чат» в основной области приложения с полной историей переписки (не только компактная панель).

#### Состав работ

- Маршрут приложения «Чат» в навигации; layout с максимальной областью под переписку.
- История и отправка через backend; согласование идентификатора диалога с задачей 06 (один диалог на пользователя/канал web или явное разделение — зафиксировать в `plan.md` задачи).
- UX: удобная прокрутка, индикатор отправки, обработка ошибок API.

#### Skills

`nextjs-app-router-patterns`, `vercel-react-best-practice`.

#### Критерии готовности (DoD)

**Для агента:**

- Страница «Чат» и плавающий чат не конфликтуют по состоянию диалога либо документировано намеренное разделение.

**Для пользователя:**

- Перейти в меню «Чат», провести диалог, сравнить с плавающей панелью согласно ожиданиям из UI-дока.

#### Документы задачи

- ✅ [План](impl/frontend/iteration-4-frontend/tasks/task-07-chat-main-route/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-07-chat-main-route/summary.md)

---

### Задача 11: Кабинет студента (зона C) ✅

**Контекст:** зона C заложена в задаче 01 и в [`docs/tech/frontend-requirements.md`](../tech/frontend-requirements.md) §6.3; API — в задаче 02 и [`api-contracts.md`](../tech/api-contracts.md). Отдельной задачи на реализацию экрана в нумерации 04–07 не было — маршрут остался заглушкой (`frontend/web/app/(app)/student/page.tsx`).

#### Цель

Страница **личного кабинета студента**: приветствие, сводка прогресса, список уроков с правилами «сдан / текущий / заблокирован», форма сдачи с `comment` и `submission_links`; только HTTP API ядра, без вызова LLM с клиента.

#### Состав работ

- [x] Прокси Next (при необходимости согласовать с уже принятым паттерном BFF): `GET .../memberships/{membership_id}/progress-overview`, `PUT .../progress-records/{checkpoint_id}` — пути под `app/api/v1/...` как у лидерборда/дашборда.
- [x] Типы ответа/запроса: отдельный модуль (например `lib/student-progress-types.ts`) по OpenAPI / фактическому JSON backend.
- [x] UI страницы `app/(app)/student/page.tsx`: шапка (имя, переход в чат — ссылка на `/chat` или открытие FAB по согласованию), блок сводки (сдано из N, следующий урок), список чекпоинтов из overview с визуальными состояниями согласно [`docs/ui/ui-requirements.md`](../ui/ui-requirements.md) экран 3.
- [x] Форма сдачи: модальное окно или inline-панель; поля отчёт и ссылки; отправка `PUT` с телом по контракту; после успеха — обновление данных (revalidate / refetch).
- [x] Ограничение «сдать только текущий» и блокировка будущих — на клиенте по `sort_order` и статусам из API, без дублирования серверных правил (403 с сервера — обработать).
- [x] Состояния loading / empty / error; для роли преподавателя на том же маршруте — понятное сообщение или редирект (если не оговорено иначе в сессии).

#### Skills

`shadcn-ui`, `vercel-react-best-practice`, `nextjs-app-router-patterns`, при расхождении с API — `api-design-principles`.

#### Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Данные кабинета с backend (mock), без заглушки «позже по roadmap» | Вход студентом из сида → открыть «Кабинет студента», сверить с `GET .../progress-overview` |
| 2 | Сдача урока: `comment` и `submission_links` уходят в `PUT .../progress-records/{checkpoint_id}`; список обновляется | Отправить форму, обновить страницу — статус урока и дата согласованы с API |
| 3 | Соответствие продуктовым требованиям зоны C | Сверка с [`frontend-requirements.md`](../tech/frontend-requirements.md) §6.3 и [`ui-requirements.md`](../ui/ui-requirements.md) экран 3 |
| 4 | Линт и сборка | `pnpm lint` / `make frontend-lint`, production build |

**Для агента:** нет прямых вызовов LLM; типы согласованы с OpenAPI при отсутствии расхождений с backend.

#### Артефакты

- `frontend/web/app/(app)/student/page.tsx` — реализация вместо заглушки.
- Новые: route handler(s) под `/api/v1/...`, компонент(ы) формы/списка, `lib/*-types.ts` при необходимости.

#### Документы задачи

- 📋 [План](impl/frontend/iteration-4-frontend/tasks/task-11-student-cabinet/plan.md)
- ✅ [Summary](impl/frontend/iteration-4-frontend/tasks/task-11-student-cabinet/summary.md)

---

### Завершение блока 3 — проверки


| Кто              | Что проверить                                                            |
| ---------------- | ------------------------------------------------------------------------ |
| **Агент**        | Все страницы работают на данных mock; нет прямых вызовов LLM из браузера |
| **Пользователь** | Сквозной сценарий: вход → дашборд / лидерборд / **кабинет студента** / чат |
| **Команды**      | При новых проверках — расширить `Makefile` (например `frontend-test`)    |


---



## Блок 4 — Задача 08: качество frontend

### Задача 08: Ревью качества кода frontend ✅

**Фактический статус:** ревью выполнено, замечания приоритезированы в [`docs/tech/technical-debt.md`](../tech/technical-debt.md). Устранение пунктов из этого файла **не сделано** — запланировано отдельно, позже.

#### Цель

Проверить код веб-клиента на соответствие best practices; устранить **критические** проблемы и недоработки.

#### Состав работ

- Пройти чеклист по skills `**vercel-react-best-practice`** и `**nextjs-app-router-patterns**` (границы RSC/Client, данные, кэш, маршруты).
- Зафиксировать найденное в `summary.md` задачи; исправить критическое (безопасность, поломка сценариев, утечки, неработающий SSR).
- Умеренные улучшения — по остаточному бюджету; не раздувать объём без необходимости.

#### Skills

`vercel-react-best-practice`, `nextjs-app-router-patterns`, `sharp-edges`.

#### Критерии готовности (DoD)

**Для агента:**

- Список проверок и результат в [summary](impl/frontend/iteration-4-frontend/tasks/task-08-frontend-quality/summary.md); критические пункты закрыты или заведены как отдельные задачи с явной пометкой (бэклог: [`technical-debt.md`](../tech/technical-debt.md)).

**Для пользователя:**

- Запустить `pnpm lint` / `make frontend-lint` и сборку; пройти основные страницы вручную после правок.

#### Документы задачи

- 📋 [План](impl/frontend/iteration-4-frontend/tasks/task-08-frontend-quality/plan.md)
- 📝 [Summary](impl/frontend/iteration-4-frontend/tasks/task-08-frontend-quality/summary.md)

---



## Блок 5 — Задачи 09–10: расширения

### Задача 09: Голосовой режим чата ⛔

**Статус:** отменена после планирования: избыточное техническое усложнение (веб: браузерные API / права / совместимость; бот и ядро: STT, лимиты, контракты, интеграции). Реализация не ведётся; приоритет не подтверждён.

Исходное описание цели и состава работ сохранено в архивном виде в [плане задачи](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/plan.md) и [summary](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/summary.md).

#### Документы задачи

- ⛔ [План / решение об отмене](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/plan.md)
- ⛔ [Summary](impl/frontend/iteration-4-frontend/tasks/task-09-voice-chat/summary.md)

---

### Задача 10: Ответы на вопросы по данным БД (Text-to-SQL) ⛔

**Статус:** не выполняется после анализа плана: избыточное усложнение (безопасный Text-to-SQL, read-only/allowlist, ADR, эксплуатация, единый pipeline для веба и бота). Реализация не ведётся; тема остаётся на дальнейшее развитие — см. [`docs/tech/technical-debt.md`](../tech/technical-debt.md) §«Отложенное развитие».

Исходная цель, варианты архитектуры и состав работ сохранены в [плане задачи](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/plan.md); итог закрытия — в [summary](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/summary.md).

#### Документы задачи

- ⛔ [План (архив)](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/plan.md)
- ⛔ [Summary](impl/frontend/iteration-4-frontend/tasks/task-10-text-to-sql/summary.md)

---

### Завершение блока 5 — проверки


| Кто              | Что проверить                                                                        |
| ---------------- | ------------------------------------------------------------------------------------ |
| **Агент**        | Задачи 09–10 отменены; при возврате к теме — заново оценить roadmap, ADR и [`technical-debt.md`](../tech/technical-debt.md) |
| **Пользователь** | —                                                                                    |
| **Команды**      | Новые цели Makefile/README при появлении отдельных сервисов или e2e-проверок         |


---

## Связанные документы (постоянная опора)

- `[docs/vision.md](../vision.md)`
- `[docs/data-model.md](../data-model.md)`
- `[docs/tech/api-contracts.md](../tech/api-contracts.md)`
- `[docs/ui/ui-requirements.md](../ui/ui-requirements.md)`
- `[docs/ui/dashboard.png](../ui/dashboard.png)` — макет панели преподавателя
- `[docs/ui/leaderboard.png](../ui/leaderboard.png)` — макет лидерборда
- `[docs/plan.md](../plan.md)`

