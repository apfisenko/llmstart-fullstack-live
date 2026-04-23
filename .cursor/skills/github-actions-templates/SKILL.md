---
name: github-actions-templates
description: >-
  Шаблоны и практики GitHub Actions: workflow YAML, jobs/steps, матрицы, кэш,
  артефакты, permissions, secrets, concurrency, reusable workflows, сервисы
  (Postgres/Redis) в CI. Используй при `.github/workflows`, CI/CD, линтерах и
  тестах в GitHub, когда пользователь упоминает GHA, GitHub Actions или CI.
  Для терминала (просмотр run, pr, `gh api`) — skill `gh-cli`.
---

# GitHub Actions — шаблоны

## Каркас workflow

- `name`, `on` (push/pull_request/workflow_dispatch/schedule), `permissions` (минимум необходимого).
- `concurrency`: группа + `cancel-in-progress: true`, чтобы не копить устаревшие прогоны.
- `jobs.<id>.runs-on`, `timeout-minutes` для долгих задач.

## Шаги

- Фиксировать версии экшенов по **commit SHA** или мажорному тегу с осознанным риском (`actions/checkout@v4` и т.п.).
- Один шаг — одна ответственность; повтор — в **composite action** или **reusable workflow**.
- `if:` на шаге/джобе для условных веток (например, только на `main`).

## Безопасность

- Явно задавать `permissions: contents: read` (и точечно `pull-requests: write` и т.д., если нужно).
- Секреты не логировать; не передавать в `run` через интерполяцию там, где возможен утечечный вывод.
- Для деплоя из форков — отдельные политики (`pull_request_target` только при крайней необходимости и с ревью рисков).

## Кэш и скорость

- Кэш зависимостей: встроенный в `setup-node` / `setup-python` / `actions/cache` с ключом по lockfile.
- Матрица `strategy.matrix` для версий ОС/рантайма; `fail-fast: false` при необходимости полного отчёта.

## Сервисы и БД в CI

- `services:` для контейнеров (образ, порты, `options: >- --health-cmd ...`).
- Переменные подключения через `env` джобы; дождаться готовности через healthcheck образа или ретраи в скрипте.

## Артефакты и отчёты

- `actions/upload-artifact` / `download-artifact` между джобами; срок хранения `retention-days` по смыслу.
- Отчёты покрытия/тестов — через официальные экшены или загрузку в хранилище, не раздувать лог.

## Проверка перед merge

- Локально сверить отступы YAML; при сомнении — валидатор или «dry» прогон на ветке.
- Для деплоя: `environment`, required reviewers, разделение staging/prod.

## Дополнительно

- OIDC в облако вместо долгоживущих ключей в секретах — когда провайдер поддерживает.
- Работа с прогонами и PR из CLI: skill **`gh-cli`** (`gh run`, `gh pr`, `gh api`).

