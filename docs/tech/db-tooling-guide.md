# Справка: инструменты БД в проекте

Руководство по ORM-моделям, Alembic и раскладке `backend/` для PostgreSQL (и локального SQLite в приложении). Архитектурные решения: [ADR-001](../adr/adr-001-database.md) (СУБД), [ADR-002](../adr/adr-002-backend-stack.md) (FastAPI, SQLAlchemy async, Alembic), [ADR-004](../adr/adr-004-db-tooling.md) (соглашения и миграции в репозитории). Целевая схема таблиц, типов и политик FK — [`data-model.md`](../data-model.md); **текущий код моделей может отличаться** до выравнивания итерацией по данным.

---

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `DATABASE_URL` | URL для SQLAlchemy. В приложении: async (`postgresql+asyncpg://...` для Postgres). Для **Alembic** переменная **обязательна**; в `backend/migrations/env.py` фрагмент `+asyncpg` заменяется на `+psycopg2` для синхронного подключения миграций. |

Пример для локального Postgres:

```text
DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/llmstart
```

В [`backend/app/config.py`](../../backend/app/config.py) для разработки без Postgres допустим дефолт SQLite (`sqlite+aiosqlite:///...`). **Alembic** при отсутствии `DATABASE_URL` завершится ошибкой — задайте URL явно перед миграциями.

Зависимости: для команд Alembic с Postgres установите dev-группу backend (`psycopg2-binary`, **`tzdata`** в `[project.optional-dependencies] dev`). Пакет **`tzdata`** нужен на **Windows**, где стандартная библиотека `zoneinfo` не содержит базу IANA; без него data-миграция с `Europe/Moscow` (ревизия `0003_seed_progress`) падает с `ZoneInfoNotFoundError`.

---

## Локальный PostgreSQL (Docker)

В корне репозитория — [`docker-compose.yml`](../../docker-compose.yml): один сервис `postgres` (образ `postgres:16-alpine`), пользователь/роль/имя БД и пароль по умолчанию **`llmstart`**, порт **`5432`**, именованный volume **`llmstart_pg_data`**, **healthcheck** через `pg_isready`.

Для Alembic и backend на **хосте** в [`DATABASE_URL`](../../backend/.env.example) указывайте `127.0.0.1`. Если backend запускается в контейнере в той же docker-сети, хост СУБД — имя сервиса **`postgres`**.

Нужны Docker Engine и **Compose V2** (`docker compose`). Цель **`make db-up`** вызывает `docker compose up -d --wait` (ожидание healthcheck). Если флаг `--wait` не поддерживается — обновите Docker Desktop / плагин compose либо поднимите контейнер вручную и дождитесь статуса healthy.

### Windows: Docker через WSL

На Windows **Docker Desktop** обычно ставит CLI в WSL2, а в PowerShell/CMD команда `docker` может отсутствовать в `PATH`. Рекомендуемый порядок:

1. В Docker Desktop: **Settings → Resources → WSL integration** — включите интеграцию для вашего дистрибутива (Ubuntu и т.д.).
2. Откройте **WSL** (тот же дистрибутив), установите в нём **`make`** и **`uv`**, клонируйте/перейдите в репозиторий по Linux-пути (например `~/projects/...` или `/mnt/c/.../llmstart-fullstack-live`). Рабочий каталог compose и путей к `data/` должен совпадать с тем, откуда вы вызываете `make`.
3. Для первого подъёма БД и миграций: **`make db-up`**, затем **`make db-migrate`**, либо сразу полный сброс — **`make db-reset`** (см. готовый сценарий ниже для проекта на **`/mnt/c/...`**). Порт `5432` проброшен на localhost — **`DATABASE_URL` с `127.0.0.1`** в `.env` остаётся верным и для процессов в WSL, и для backend на Windows, если он подключается к тому же хосту.

#### WSL: готовая последовательность для `make db-reset` (проект на `/mnt/c/...`)

Если репозиторий лежит на диске Windows, перед **`make db-reset`** (и вообще перед **`uv sync`** в `backend/`) задайте **`PATH`** (чтобы находился **`uv`**, если он установлен в `~/.local/bin`) и **`UV_PROJECT_ENVIRONMENT`** на каталог **ext4** в домашней директории WSL — иначе см. подраздел про ошибку **`.venv/Scripts`** ниже.

Подставьте в **`cd`** свой путь; пример: `/mnt/c/FISENKO/ИИ/llmstart-fullstack-live`.

```bash
export PATH="$HOME/.local/bin:$PATH"
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/llmstart-backend"
mkdir -p "$HOME/.venvs"
cd "/mnt/c/путь/к/llmstart-fullstack-live"
make db-reset
```

Эта последовательность: поднимает Postgres через **`docker compose`**, сбрасывает volume, применяет миграции Alembic до **`head`**.

Если по какой-то причине нужно вызывать **Make из Windows**, а Docker — только в WSL, переопределите переменную в [Makefile](../../Makefile):

```bash
make db-up DOCKER_COMPOSE="wsl -e docker compose"
```

(имя дистрибутива при необходимости: `wsl -d Ubuntu -e docker compose ...` — всё в одной строке значения `DOCKER_COMPOSE`). В этом смешанном режиме **`db-migrate`** всё равно выполняется в среде, откуда запущен `make` (Windows), поэтому там должен быть **uv** и доступ к `127.0.0.1:5432`. Проще и стабильнее держать и Docker, и **uv**, и **make** в одной среде — **внутри WSL**.

### WSL: репозиторий на `/mnt/c/...` и ошибка `uv sync` / `.venv/Scripts`

Если проект лежит на диске Windows (`/mnt/c/...`), а **`backend/.venv`** когда‑то создавали из **Windows**, в WSL команда **`make db-reset`** (и любой **`uv sync`** в `backend/`) может завершиться ошибкой вроде **`failed to remove directory .../.venv/Scripts: Input/output error`** — смесь раскладки venv (каталог `Scripts`) и файловой системы **drvfs** даёт сбой при пересборке окружения под Linux.

**Варианты:**

1. Держать виртуальное окружение **на ext4** — используйте готовую последовательность команд в подразделе **«WSL: готовая последовательность для `make db-reset`»** выше (`PATH`, `UV_PROJECT_ENVIRONMENT`, `cd`, `make db-reset`).

2. Клонировать репозиторий в **`~/projects/...`** внутри WSL и работать оттуда (и venv, и `uv` — на ext4); тогда **`UV_PROJECT_ENVIRONMENT`** обычно не нужен, достаточно **`cd`** в корень клона и **`make db-reset`**.

3. Удалить **`backend/.venv`** только из **Windows** (Explorer / PowerShell), затем снова выполнить **`uv sync`** из WSL — иногда достаточно, но при смешанном использовании Windows/WSL надёжнее вариант 1 или 2.

### Смешанный режим: только Docker в WSL, `uv` на Windows

Типично: в WSL есть `docker compose`, но нет **`make`** / **`uv`**; на Windows установлен **`uv`**. Тогда:

1. Поднять Postgres из WSL (путь к репозиторию — Linux, см. `/mnt/c/...` или клон в `$HOME`):

   ```bash
   wsl -e bash -lc 'cd "/mnt/c/путь/к/llmstart-fullstack-live" && docker compose up -d --wait'
   ```

   Полный сброс volume + миграции (аналог `make db-reset`), если в WSL есть `make` и `uv`. Для репозитория на **`/mnt/c/...`** задайте **`UV_PROJECT_ENVIRONMENT`** (см. подраздел выше), иначе `uv sync` может упасть на `.venv/Scripts`:

   ```bash
   wsl -e bash -lc 'export PATH="$HOME/.local/bin:$PATH" && export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/llmstart-backend" && mkdir -p "$HOME/.venvs" && cd "/mnt/c/путь/к/llmstart-fullstack-live" && make db-reset'
   ```

2. **Миграции Alembic с Windows** (порт `5432` проброшен на localhost):

   ```powershell
   $env:DATABASE_URL = "postgresql+asyncpg://llmstart:llmstart@127.0.0.1:5432/llmstart"
   cd backend
   uv sync --extra dev
   uv run alembic upgrade head
   uv run alembic current
   ```

   Ожидаемая строка `alembic current`: ревизия **`0004_dialogue_turns (head)`** (или актуальная голова цепочки).

3. **Pytest** по умолчанию поднимает **отдельную SQLite in-memory** схему (см. `tests/conftest.py`), чтобы не конфликтовать с сидом в PostgreSQL. Перед запуском тестов **сбросьте** `DATABASE_URL` в сессии, если вы только что задавали её для Alembic:

   ```powershell
   Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
   cd backend
   uv run pytest
   ```

   Цель **`make test-backend`** из корня репозитория делает то же (без принудительного Postgres в env).

---

## Make: команды для БД

Команды выполняются из **корня репозитория** (нужен GNU Make; на Windows удобнее **WSL**, а не только Git Bash, если Docker живёт в WSL).

По умолчанию цели `db-up` / `db-down` / `db-reset` / `db-shell` используют **`docker compose`**; при необходимости задайте **`DOCKER_COMPOSE`** (см. раздел «Docker через WSL» выше).

| Цель | Действие |
|------|----------|
| `make db-up` | `docker compose up -d --wait` (или `$(DOCKER_COMPOSE) …`) |
| `make db-down` | `docker compose down` (данные в volume по умолчанию сохраняются) |
| `make db-reset` | `docker compose down -v`, снова `up --wait`, затем миграции до `head` |
| `make db-migrate` | `cd backend && uv sync --extra dev && uv run alembic upgrade head` |
| `make db-shell` | `psql` внутри контейнера `postgres` |
| `make migrate-backend` | синоним **`make db-migrate`** |

**`DATABASE_URL`** для рецептов миграций: если переменная уже задана в окружении, Makefile её не меняет (`?=`). Иначе подставляется URL под дефолтный compose: `postgresql+asyncpg://llmstart:llmstart@127.0.0.1:5432/llmstart`. Параметры `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` в Makefile можно переопределить в командной строке, если изменили `docker-compose.yml` — см. [Makefile](../../Makefile). Переменная **`DOCKER_COMPOSE`** задаёт префикс вызова Compose (см. раздел про WSL).

---

## Структура каталогов (backend)

Согласовано с [conventions](../../.cursor/rules/conventions.mdc):

| Путь | Назначение |
|------|------------|
| `backend/alembic.ini` | Корень Alembic; `script_location = migrations` (пути относительно `backend/`). |
| `backend/migrations/env.py` | Подключение к БД, `target_metadata` из ORM. |
| `backend/migrations/versions/` | Файлы ревизий Alembic. |
| `backend/migrations/script.py.mako` | Шаблон новых ревизий (`alembic revision`). |
| `backend/app/domain/base.py` | `DeclarativeBase` — корень ORM, `Base.metadata` для Alembic. |
| `backend/app/domain/models.py` | Классы моделей и перечисления домена. |
| `backend/app/infrastructure/` | Async-движок, сессия, репозитории (по мере появления). |
| `backend/app/api/deps.py` | Общие Depends, в т.ч. сессия БД. |

---

## ORM-модели

### База и метаданные

- В [`backend/app/domain/base.py`](../../backend/app/domain/base.py) объявлен **`Base`** — наследник `sqlalchemy.orm.DeclarativeBase` без дополнительных миксинов.
- Все таблицы проекта регистрируются на **`Base.metadata`**. Именно этот объект передаётся в Alembic как **`target_metadata`** в [`env.py`](../../backend/migrations/env.py).

### Где лежат модели

- Основной модуль — [`backend/app/domain/models.py`](../../backend/app/domain/models.py): один файл с классами сущностей и Python-перечислениями для полей со статичным набором значений.
- Импорт для побочного эффекта регистрации таблиц: в `env.py` выполняется `from app.domain import models` (после импорта `Base`), чтобы все классы успели подписаться на `metadata` до чтения `Base.metadata`.

### Стиль SQLAlchemy 2.x

- Объявление колонок — **`Mapped[...]`** и **`mapped_column(...)`**, связи — **`relationship(...)`** с `back_populates` для двунаправленных связей.
- Первичные ключи — **`Uuid(as_uuid=True)`**, значение по умолчанию **`default=uuid.uuid4`** на стороне приложения (для миграций при `create_all` поведение зависит от диалекта; для Postgres целевая схема в `data-model.md` допускает `gen_random_uuid()` на уровне БД — см. миграции при сближении с документом).
- Строки фиксированной длины в модели задаются через **`String(n)`**; длинный текст — **`Text`**.
- Время — **`DateTime(timezone=True)`** (в БД соответствует `TIMESTAMP WITH TIME ZONE` / аналог).
- Внешние ключи — **`ForeignKey("таблица.колонка", ondelete="...")`**; в текущем коде часто **`CASCADE`** — при эволюции схемы сверяйте с [`data-model.md`](../data-model.md) (там для части связей задан **`RESTRICT`**).

### Имена таблиц и ограничения

- Имя таблицы задаётся явно: **`__tablename__ = "..."`** в snake_case, множественное число (`users`, `cohort_memberships`, …).
- Составные уникальные ограничения — **`__table_args__ = (UniqueConstraint(..., name="..."),)`**, например одна пара пользователь–поток, одна пара участие–чекпоинт для прогресса.

### Перечисления (enum)

- В коде — стандартные **`enum.Enum`** (часто с наследованием от `str` для значений), в колонке — **`sqlalchemy.Enum` как `SAEnum(..., name="...", native_enum=False)`**.
- **`native_enum=False`** означает, что в БД не создаётся отдельный тип PostgreSQL ENUM из этого объявления ORM; хранение согласуется с фактическими миграциями. Целевая физическая модель в **`data-model.md`** описывает **нативные PG ENUM** — при приведении схемы к документу понадобятся ревизии Alembic и, при необходимости, смена параметров `SAEnum` / явный DDL.

### Связи (`relationship`)

- Примеры: `User.memberships` ↔ `CohortMembership.user`, `Cohort.memberships` / `checkpoints`, `Dialogue.turns` с **`order_by`** для ходов по `asked_at`.
- Имена атрибутов в Python — в стиле кода (`membership_id`, `checkpoint_id`); они **не обязаны** совпадать с именами колонок в `data-model.md`, пока документ и миграции не унифицированы (`cohort_membership_id` vs `membership_id` и т.д.).

### Текущий набор сущностей в коде (ориентир)

| Класс модели | Таблица | Назначение (кратко) |
|--------------|---------|---------------------|
| `User` | `users` | пользователь, `name`, `telegram_user_id` |
| `Cohort` | `cohorts` | поток, `title`, `code`, период |
| `CohortMembership` | `cohort_memberships` | участие, роль, статус |
| `Dialogue` | `dialogues` | диалог в рамках участия, канал, состояние |
| `DialogueTurn` | `dialogue_turns` | одна пара вопрос/ответ (`question_text`, `answer_text`, `asked_at`, `answered_at`; два UUID: `id`, `assistant_message_id`) |
| `ProgressCheckpoint` | `progress_checkpoints` | этап прогресса потока |
| `ProgressRecord` | `progress_records` | отметка прогресса по участию и чекпоинту |

Репозитории (доступ к данным под сценарии API): `app/infrastructure/repositories/` — `DialogueRepository`, `CohortProgressRepository`; сервисы в `app/services/` остаются оркестрацией и правами.

Миграция **`0004_dialogue_turns`**: перенос данных из устаревшей таблицы `dialogue_messages` (если была) и переход на `dialogue_turns`.

### Async runtime (кратко)

- Приложение использует **async**-сессию и движок (см. `app/infrastructure/` и [ADR-002](../adr/adr-002-backend-stack.md)); модели те же, что видит Alembic через `metadata`. Не смешивайте в одном запросе к БД синхронный `Session` из стека миграций с async-хендлерами FastAPI.

---

## Alembic: миграции

### Роль и одна точка правды

- **Alembic** — единственный поддерживаемый способ менять схему БД под приложение. Версия «голова» цепочки должна соответствовать ожиданиям кода ORM и сервисов в той же ветке.
- Служебная таблица **`alembic_version`** хранит идентификатор применённой ревизии (одна строка при линейной истории).

### `env.py`: метаданные и подключение

Файл [`backend/migrations/env.py`](../../backend/migrations/env.py):

1. Загружает конфиг из `alembic.ini`.
2. Импортирует **`Base`** и **`app.domain.models`**, чтобы все модели зарегистрировались.
3. Устанавливает **`target_metadata = Base.metadata`** — по нему можно строить autogenerate и согласовывать состав таблиц с ORM.
4. **`_sync_database_url()`** читает **`DATABASE_URL`**; при отсутствии — `RuntimeError`. Подстрока **`+asyncpg`** заменяется на **`+psycopg2`** для **`create_engine`** (синхронное подключение).
5. Режимы **`run_migrations_offline()`** (URL в конфиге контекста) и **`run_migrations_online()`** (подключение через `create_engine`, `pool.NullPool`) — стандартный шаблон Alembic.

Любой новый драйвер или формат URL потребует правки **`_sync_database_url()`** и обновления этой справки.

### Файл ревизии: обязательные поля

Каждый файл в `versions/` содержит:

| Поле | Смысл |
|------|--------|
| `revision` | Уникальная строка-ID ревизии (в проекте — осмысленные id вроде `0001_initial`, `0002_user_name`, `0003_seed_progress`). |
| `down_revision` | ID родительской ревизии или `None` только у первой в цепочке. |
| `branch_labels`, `depends_on` | Обычно `None`; `depends_on` — для межветочных зависимостей. |
| `upgrade()` / `downgrade()` | Тело миграции вперёд и откат. |

Имя файла желательно согласовать с `revision` и смыслом: шаблон **`NNNN_short_slug.py`**.

### Паттерны в этом репозитории

**1. Первая ревизия через метаданные ORM**

[`0001_initial_schema.py`](../../backend/migrations/versions/0001_initial_schema.py):

- В **`upgrade()`** вызывается **`Base.metadata.create_all(bind=op.get_bind())`** — таблицы создаются по текущему состоянию моделей на момент ревизии.
- В **`downgrade()`** — **`drop_all`** — уничтожает все таблицы из metadata (осторожно на общей БД).

Плюс: быстрый старт. Минус: дальнейшие изменения схемы не должны молча править только модели без новой ревизии — иначе расхождение с уже развёрнутыми БД.

**2. Последующие ревизии — явный DDL**

Пример: [`0002_rename_users_display_name_to_name.py`](../../backend/migrations/versions/0002_rename_users_display_name_to_name.py) — **`op.alter_column`**, проверка колонок через **`sa.inspect(bind)`**, чтобы миграция была идемпотентной на разных состояниях стенда.

Рекомендуемый путь для зрелой схемы: **`op.create_table`**, **`op.add_column`**, **`op.create_index`**, **`op.execute`** для сложного SQL, с осмысленным **`downgrade`**.

**3. Data migration / сид из JSON**

[`0003_seed_course_progress.py`](../../backend/migrations/versions/0003_seed_course_progress.py): читает [`data/progress-import.v1.json`](../../data/progress-import.v1.json) (путь от `backend/migrations/versions/` — три уровня вверх до корня репозитория), заполняет поток, пользователей, участия, чекпоинты и записи прогресса. В JSON поле `progress_status: "done"` сохраняется как **`completed`** в БД (как в OpenAPI). Время `submitted_at` без таймзоны трактуется как **Europe/Moscow** (см. комментарий в ревизии и `meta` JSON).

Цепочка ревизий: `0001_initial` → `0002_user_name` → **`0003_seed_progress`**. В декомпозиции [tasklist-database](../tasks/tasklist-database.md) изначально фигурировали номера «0001/0002» под схему и сид; фактически сид — **третья** ревизия, так как `0002` заняла переименование колонки пользователя.

**4. Autogenerate (опционально)**

Команда:

```bash
cd backend && uv run alembic revision --autogenerate -m "описание"
```

Сравнивает **`target_metadata`** с живой БД и генерирует черновик. Его **обязательно** просматривают: autogenerate не умеет всё (переименования колонок, данные, частичные индексы, смена типа ENUM), часто создаёт лишние `drop`/`create`. После генерации выровняйте **`revision`** / **`down_revision`** и имя файла под принятый стиль.

### Команды Alembic

Выполняйте из **`backend/`** после **`uv sync --extra dev`** (для Postgres).

| Действие | Команда |
|----------|---------|
| Применить все ревизии до головы | `uv run alembic upgrade head` |
| Из корня репозитория (то же + sync) | `make db-migrate` или `make migrate-backend` |
| Текущая ревизия | `uv run alembic current` |
| История | `uv run alembic history` |
| Новая пустая ревизия | `uv run alembic revision -m "краткое_описание"` |
| Откат на одну ревизию | `uv run alembic downgrade -1` |
| Autogenerate (с осторожностью) | `uv run alembic revision --autogenerate -m "описание"` |

### Рабочий процесс при изменении модели

1. Изменить **`models.py`** (и при необходимости **`data-model.md`** по согласованию).
2. Добавить файл в **`migrations/versions/`**: либо autogenerate + ручная правка, либо ручной `op.*`.
3. Проверить **`upgrade head`** на чистой БД и на копии стенда с данными.
4. Закоммитить ревизию вместе с кодом, который рассчитывает на новую схему.

Подробнее про политику ветвления и согласование с ADR — [ADR-004](../adr/adr-004-db-tooling.md), раздел «Управление миграциями».

---

## Соглашения по именам

- **Таблицы:** множественное число, `snake_case` — как в [`data-model.md`](../data-model.md).
- **Ревизии Alembic:** стабильный `revision = "..."` и осмысленное имя файла (например `0002_rename_users_display_name_to_name.py`).

---

## Проверка после `upgrade head`

Базово:

```sql
\dt
SELECT * FROM alembic_version;
```

После **`make db-reset`** (чистый volume + все миграции включая сид) в **`make db-shell`** ожидаются данные из `progress-import.v1.json`:

```sql
-- голова цепочки Alembic
SELECT version_num FROM alembic_version;
-- ожидается: 0003_seed_progress

-- поток
SELECT title FROM cohorts WHERE title = 'M05 LLM Start Fullstack';

-- 13 студентов (роль student в этом потоке)
SELECT COUNT(*) FROM cohort_memberships m
JOIN cohorts c ON c.id = m.cohort_id
WHERE c.title = 'M05 LLM Start Fullstack' AND m.role = 'student';

-- 3 чекпоинта (урока/ДЗ)
SELECT COUNT(*) FROM progress_checkpoints ck
JOIN cohorts c ON c.id = ck.cohort_id
WHERE c.title = 'M05 LLM Start Fullstack';

-- 24 отметки прогресса в статусе completed (в импорте было "done")
SELECT COUNT(*) FROM progress_records pr
JOIN cohort_memberships m ON m.id = pr.membership_id
JOIN cohorts c ON c.id = m.cohort_id
WHERE c.title = 'M05 LLM Start Fullstack' AND pr.status = 'completed';
```

Тот же набор запросов собран в [`scripts/pg-selftest.sql`](../../scripts/pg-selftest.sql). Из корня репозитория (в т.ч. в WSL):

```bash
docker compose exec -T -e PGPASSWORD=llmstart postgres \
  psql -U llmstart -d llmstart -v ON_ERROR_STOP=1 < scripts/pg-selftest.sql
```

---

## Связанные документы

- [`docs/data-model.md`](../data-model.md)
- [`docs/adr/adr-004-db-tooling.md`](../adr/adr-004-db-tooling.md)
- [`Makefile`](../../Makefile) — цели `db-*` и `migrate-backend`
- [`docker-compose.yml`](../../docker-compose.yml)
- [`scripts/pg-selftest.sql`](../../scripts/pg-selftest.sql)
