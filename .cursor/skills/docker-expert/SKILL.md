---
name: docker-expert
description: >-
  Dockerfile, multi-stage, BuildKit, .dockerignore, Compose, non-root,
  healthcheck, кэш слоёв, multi-arch, сети и тома. Используй при контейнеризации
  приложений, отладке образов, CI build/push, когда пользователь упоминает
  Docker, docker-compose, контейнер или образ.
---

# Docker — практики

## Dockerfile

- **Multi-stage**: финальный образ без toolchain и исходников сборки; копировать только артефакты (`COPY --from=...`).
- Порядок слоёв: редко меняющееся (зависимости, системные пакеты) **выше**, код и конфиги частой смены — **ниже** для кэша.
- Пиновать базовый образ: тег + при необходимости digest; избегать `latest` в проде.
- **`.dockerignore`**: как `.gitignore`, плюс `node_modules`, `.git`, артефакты сборки, локальные `.env` — чтобы контекст был маленьким и детерминированным.

## Безопасность и рантайм

- Не запускать процесс от root без причины: `USER` после установки пакетов; права на файлы через `chown` в нужном stage.
- Минимизировать пакеты в образе; не хранить секреты в слоях — `ARG` для CI, runtime — через env/secret orchestrator.
- `HEALTHCHECK` для долгоживущих сервисов; в Kubernetes предпочтительны probes, но в чистом Docker healthcheck полезен.

## BuildKit

- Включён по умолчанию в современном Docker; `RUN --mount=type=cache` для ускорения установки зависимостей.
- Multi-arch: `docker buildx build --platform linux/amd64,linux/arm64` при необходимости публикации.

## Compose

- Явные `depends_on` не ждут «готовности» сервиса без healthcheck; для БД — healthcheck + condition или скрипт ожидания.
- Именованные тома для данных БД; не монтировать весь репозиторий в прод-контейнер без нужды.
- Переменные через `.env` рядом с compose или `env_file`; не коммитить секреты.

## Отладка

- `docker build --progress=plain` для полного лога слоёв; `docker run --rm -it` для интерактива.
- Размер образа: `docker history`, dive-подобные инструменты по ситуации.

## CI

- Кэш билдера (`cache-from` / `cache-to` в buildx) для ускорения; push только после успешных тестов.
