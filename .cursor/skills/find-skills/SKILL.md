---
name: find-skills
description: >-
  Находит и выбирает релевантные Agent Skills в репозитории. Используй при
  старте незнакомой задачи, когда пользователь просит «какой skill применить»,
  или перед крупными изменениями в API, тестах, FastAPI, UI (shadcn) или
  Next.js/Vercel (`vercel-react-best-practice`, маршруты App Router —
  `nextjs-app-router-patterns`); при неочевидных багах и расхождениях окружений —
  `sharp-edges`; для CI в GitHub (YAML) — `github-actions-templates`, из терминала
  — `gh-cli`; для Docker и Compose — `docker-expert`.
---

# Поиск skills в проекте

## Где лежат

- **Проектные skills**: `.cursor/skills/<имя>/SKILL.md` (в репозитории, общие для команды).
- Встроенные skills Cursor не хранить и не править в `~/.cursor/skills-cursor/`.

## Как выбрать

1. Список каталогов: `glob` или обход `.cursor/skills/*/SKILL.md`.
2. Прочитать YAML `description` в frontmatter — там сценарии применения (WHEN) и возможности (WHAT).
3. Читать полный `SKILL.md` только для выбранных тем; при необходимости — связанные `reference.md` / `examples.md` на один уровень вложенности.

## Когда применять этот skill

- Нужно быстро понять, есть ли в проекте готовые правила под задачу.
- Пользователь добавил новые skills — пересканировать каталог перед работой.
