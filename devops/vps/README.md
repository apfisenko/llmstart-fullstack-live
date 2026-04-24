# VPS: подготовка хоста (Debian / Ubuntu)

Скрипты для **воспроизводимой** первичной настройки сервера под [ручной деплой из GHCR](../../docs/tech/vps-manual-ghcr-deploy.md): Docker Engine, **Compose plugin** v2 (`docker compose`, в т.ч. флаг `--wait` в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml)), `git`, `curl`.

## Порядок: сначала клон, потом bootstrap

1. **На VPS** — `git clone` репозитория в выбранный каталог (подробно: [vps-manual-ghcr-deploy.md §2](../../docs/tech/vps-manual-ghcr-deploy.md#2-копирование-репозитория-на-vps)). В клоне должны оказаться `docker-compose.ghcr.yml` и `devops/vps/bootstrap-debian-ubuntu.sh`.
2. **Из корня клона** — запуск скрипта ниже.

Если клон сделать нельзя, можно **скопировать** только `devops/vps/bootstrap-debian-ubuntu.sh` (например `scp` с ПК) и запустить его — для полноценного compose всё равно понадобятся `docker-compose.ghcr.yml` и `devops/postgres/…`; предпочтителен полный клон.

## Что делает `bootstrap-debian-ubuntu.sh`

- Подключает официальный репозиторий Docker (см. [установка Engine](https://docs.docker.com/engine/install/)) и ставит пакеты: `docker-ce`, `docker-compose-plugin` и др.
- Включает сервис `docker`.
- Если скрипт запущен через `sudo`, добавляет `SUDO_USER` в группу `docker` (потом может понадобиться `newgrp docker` или новый SSH-сеанс).

**Не делает:** `docker login`, UFW, открытие портов в облачной панели — это в [vps-manual-ghcr-deploy.md](../../docs/tech/vps-manual-ghcr-deploy.md).

## Запуск (из корня клонированного репозитория)

```bash
cd /opt/llmstart   # замените на путь к корню вашего клона
chmod +x devops/vps/bootstrap-debian-ubuntu.sh
sudo ./devops/vps/bootstrap-debian-ubuntu.sh
```

Поддерживаются **Debian** и **Ubuntu** с непустым `VERSION_CODENAME` в `/etc/os-release` (типичные образы Timeweb / облака).
