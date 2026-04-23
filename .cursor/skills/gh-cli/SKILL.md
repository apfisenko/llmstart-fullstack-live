---
name: gh-cli
description: >-
  GitHub CLI (gh): аутентификация, репозитории, issues, PR, проверки, просмотр и
  перезапуск workflow runs, работа с `gh api`. Используй при отладке CI,
  работе с PR/issue из терминала, скриптах вокруг GitHub, когда пользователь
  упоминает gh, GitHub CLI или `gh` в shell.
---

# GitHub CLI (`gh`)

## Установка и вход

- Установка: [cli.github.com](https://cli.github.com/) или пакетный менеджер ОС.
- `gh auth login` — выбрать `github.com`, протокол HTTPS/SSH, способ (браузер или token).
- `gh auth status` — какой хост/аккаунт активен. `gh auth token` — для скриптов (осторожно с логами).

## Репозиторий и контекст

- `gh repo view` / `gh repo view owner/name` — описание, default branch, URL.
- В каталоге с `git` remote `origin` — контекст по умолчанию; иначе `-R owner/repo`.

## Issues и PR

- `gh issue list` / `gh issue view <n>` / `gh issue create`.
- `gh pr list` / `gh pr view` / `gh pr create` / `gh pr merge` (флаги по политике репо).
- `gh pr checks` — статусы checks по текущему/указанному PR.

## Actions (CI)

- `gh run list` — недавние runs; `gh run list --workflow=<name.yml>`.
- `gh run view <id>` — логи, шаги; `--log` / `--log-failed` для вывода.
- `gh run rerun <id>` / `gh run download <id>` (артефакты, если права).
- `gh workflow list` / `gh workflow run <name>` (ручной запуск при `workflow_dispatch`).

## Низкоуровневый API

- `gh api` — GraphQL/REST, например `gh api user`, `gh api repos/{owner}/{repo}/...`.
- Удобно для автоматизации, чего нет в подкомандах; смотри [REST](https://docs.github.com/en/rest) / схемы.

## Скрипты и CI

- В GitHub Actions job с `gh`: обычно `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` + `gh ...` (или `gh api`), права `permissions` сузить, но дать нужное (например `pull-requests: write`).

## Связь с GHA

- Правка YAML — см. skill **`github-actions-templates`**; `gh` — для проверки прогонов и PR с машины.
