# DevOps Tasklist

## Обзор

Подготовительная часть DevOps: локальный полный стек в Docker, единый `docker-compose`, удобные команды и документация; затем сборка и публикация образов в **GitHub Container Registry (GHCR)** через GitHub Actions. **Полноценный CI/CD** (автодеплой в прод, секреты окружений, observability) — **следующие итерации**, вне объёма этого файла.

## Легенда статусов

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| Итерация 1 | Локальный полный стек: `devops/`, Dockerfile, корневой compose, команды, инструкция, обновление проектных docs | ✅ | [блок](#iteration-1-local-stack) |
| Итерация 2 | GitHub Actions: сборка и push образов в GHCR; compose из registry; проверка локального запуска | ✅ | [блок](#iteration-2-ghcr) |

---

## Итерация 1: локальный полный стек {#iteration-1-local-stack}

### Цель

Разработчик поднимает **PostgreSQL отдельно** или **весь стек** (backend, веб, бот, БД) из одного корневого `docker-compose.yml`, с воспроизводимыми образами, понятной структурой `devops/` и командами в `tasks.ps1` / `Makefile`.

### Состав работ

- [x] Спроектировать и описать в `devops/README.md` структуру артефактов: базовый каталог `devops/`, вложенность по сервисам (`devops/backend/`, `devops/bot/`, `devops/web/` — Dockerfile; контекст сборки — корень, единый [`.dockerignore`](../../.dockerignore)); связь с корневым [docker-compose.yml](../../docker-compose.yml).
- [x] Зафиксировать схему для **PostgreSQL**: init в [`devops/postgres/`](../../devops/postgres/); каталог [`docker/postgres/`](../../docker/postgres/) — редирект в README без дублирования SQL.
- [x] Добавить **Dockerfile** для backend, bot, web (Next.js multi-stage; Python — uv; секреты не в образах). **`.dockerignore`** — один в корне репозитория (см. `devops/README.md`).
- [x] Расширить **корневой** `docker-compose.yml`: полный стек в **одном** файле; сервис `postgres` — единый источник правды для режима «только БД» и для полного стека.
- [x] Обеспечить **отдельный запуск только БД** без приложений: профиль **`app`** для приложений; `postgres` без профиля; `db-up` / `db-down` — только Postgres + миграции с хоста по документации.
- [x] Расширить [tasks.ps1](../../tasks.ps1) и [Makefile](../../Makefile): `stack-up` / `stack-down`, `stack-status`, `stack-logs`, `check-backend`, `check-web`, `check-bot` (согласованные имена).
- [x] Ревью docker-конфигурации по skill **`docker-expert`**: замечания и итог — секция «Docker review notes» в [`devops/README.md`](../../devops/README.md).
- [x] Создать инструкцию [docker-compose-local.md](../tech/docker-compose-local.md): env, порядок `up`, миграции, проверки backend / web / bot.
- [x] Обновить проектную документацию: [architecture.md](../architecture.md), [onboarding.md](../onboarding.md), [README.md](../../README.md); в [plan.md](../plan.md) — итерация 6 и ссылки на этот tasklist.

### Definition of Done

**Для агента (self-check)**

- `devops/README.md` объясняет структуру и отсутствие дублирования compose-файлов «только БД» при отдельной процедуре `db-up`.
- `docker compose config` проходит без ошибок; `docker compose up` поднимает согласованный набор сервисов; **только postgres** поднимается отдельной документированной командой / профилями без ручного редактирования YAML «на лету».
- Существуют Dockerfile и `.dockerignore` для backend, bot, web; образы собираются из корня репозитория ожидаемыми путями.
- `tasks.ps1` и `Makefile` содержат согласованные цели: отдельно БД и отдельно полный стек + диагностика (`status`, `logs`) и **отдельные команды проверки для backend, frontend и bot** (ожидаемый успешный выход задокументирован).
- Ревью **docker-expert** выполнено, итог отражён (в PR или в summary задачи).
- Создан файл инструкции в `docs/tech/`; обновлены `architecture.md`, `onboarding.md`, при необходимости README и `plan.md`.

**Для пользователя (user-check)**

- По инструкции можно поднять **только** PostgreSQL и подключить к нему backend на хосте (как раньше с `db-up`).
- По инструкции можно поднять **полный стек** и по отдельности убедиться, что **backend**, **frontend** и **bot** отвечают ожидаемо (команды из tasklist/инструкции).
- Команды в `.\tasks.ps1 help` и `make`/`make help` понятны без чтения исходников compose.

### Артефакты (целевые)

- `devops/**` — README, Dockerfile/`.dockerignore` по сервисам (и при переносе — postgres).
- [docker-compose.yml](../../docker-compose.yml) — расширенный манифест.
- [tasks.ps1](../../tasks.ps1), [Makefile](../../Makefile) — цели для БД и полного стека.
- `docs/tech/docker-compose-local.md` (имя при согласовании можно уточнить).
- Обновления: [architecture.md](../architecture.md), [onboarding.md](../onboarding.md), [plan.md](../plan.md).

---

## Итерация 2: образы в GHCR и локальная проверка {#iteration-2-ghcr}

### Цель

Образы backend, bot и web **собираются в CI** и публикуются в **GHCR**; локально можно поднять проект **с образов из registry**, без обязательной локальной `docker build` для ежедневной проверки.

### Состав работ

- [x] Добавить workflow GitHub Actions по skill **`github-actions-templates`**: job(ы) с `docker build` и `docker push` в `ghcr.io/<owner>/<repo>/...`; permissions `packages: write`; теги минимум **`latest`** для default branch и **`sha`** (или semver при релизах — зафиксировать в workflow/README пакета).
- [x] Документировать имена образов и теги (в `devops/README.md`, инструкции или `docs/tech/`).
- [x] Подготовить сценарий Compose **из опубликованных образов** (override-файл, отдельный compose-фрагмент или `profiles` — один понятный способ «как на registry») и провести **ревью** этой конфигурации (в т.ч. через **docker-expert** при существенных отличиях от локального build).
- [x] Проверить: полный подъём стека **только из образов GHCR** (переменные/registry login при необходимости задокументировать).

### Definition of Done

**Для агента (self-check)**

- Workflow успешно выполняется на целевой ветке; в GHCR видны ожидаемые репозитории образов и теги.
- Документация содержит точные имена `image:` и способ логина к GHCR для `docker pull` при приватном пакете.
- `docker compose` с образами из registry поднимает сервисы; миграции/порядок старта согласованы с итерацией 1.
- Ревью compose «из registry» выполнено, замечания учтены.

**Для пользователя (user-check)**

- После успешного CI на основной ветке образы появляются в GHCR и их можно найти по инструкции.
- Склонировав репозиторий и задав теги env (если нужно), можно поднять стек **без** локальной сборки приложений.

### Артефакты (целевые)

- `.github/workflows/*.yml` — сборка и публикация в GHCR.
- Документ(ы) с тегами и примером `compose` из registry.
- При необходимости — `docker-compose.override.yml` / отдельный yaml для registry (как принято в репозитории после итерации 1).

---

## Вне scope этих двух итераций

- Production-deploy, управление секретами прод, Kubernetes/Helm, полный CD-пайплайн, алерты/мониторинг — последующие этапы roadmap.
