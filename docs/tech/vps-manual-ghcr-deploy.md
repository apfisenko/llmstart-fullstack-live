# VPS: ручной деплой стека из GHCR

Пошаговый сценарий для **воспроизводимой** настройки хоста (Debian/Ubuntu) и подъёма того же стека, что в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml), **без** автоматического CD (он — [итерация 5 в tasklist-devops.md](../tasks/tasklist-devops.md#iteration-5-cd-gha)).

**Политика:** в git **не** попадают токены, приватные ключи и прод-`.env`. Этот файл содержит только **шаблоны команд**; подставляете значения **на сервере** сами.

**Связанные документы:** [timeweb-vps.md](timeweb-vps.md) (VPS, SSH, `twc`), [docker-compose-ghcr.md](docker-compose-ghcr.md) (имена образов, теги, локальные нюансы), bootstrap — [devops/vps/README.md](../../devops/vps/README.md).

## Краткий порядок (рекомендуемая цепочка)

1. [§1 — предварительно](#1-предварительно) (SSH, при необходимости PAT к GHCR).
2. [§2 — копирование репозитория на VPS](#2-копирование-репозитория-на-vps) (`git clone` в фиксированный каталог — **сначала появляется дерево с `docker-compose.ghcr.yml` и `devops/vps/…`**).
3. [§3 — установка Docker (bootstrap)](#3-установка-docker-и-утилит-bootstrap) (скрипт из **уже** склонированного клона).
4. [§4 — env](#4-файлы-окружения-только-на-сервере) → [§5 — ручной login GHCR](#5-ручной-docker-login-ghcrio-выполняет-владелец-на-сервере) → [§6 — compose](#6-запуск-стека) → [§7 — фаервол](#7-фаервол-и-доступ-снаружи) → [§8 — проверки](#8-проверки-api-и-браузер).

---

## 1. Предварительно

1. **SSH** на сервер (персональный ключ, см. [timeweb-vps.md](timeweb-vps.md)).
2. **Репозиторий** на GitHub: видимость пакетов в GHCR (**Settings → Packages**). Если пакеты **публичные** — `docker pull` **без** `docker login` (см. [§5](#5-ручной-docker-login-ghcrio-выполняет-владелец-на-сервере)).
3. Для **приватных** пакетов: [Personal Access Token](https://github.com/settings/tokens) с правом **`read:packages`** (классический PAT) **или** fine-grained с доступом к репозиторию и чтению пакетов. Срок действия токена ограничьте; по истечении — выпустить новый и **повторить** логин в Docker ([§5](#5-ручной-docker-login-ghcrio-выполняет-владелец-на-сервере)).
4. Для **приватного** исходного репо на GitHub: нужен способ `git clone` (SSH-ключ на сервере, разрешённый в GitHub, **или** HTTPS с [PAT/паролем](https://docs.github.com/en/authentication) — **не** коммитить в URL).

## 2. Копирование репозитория на VPS

**Рекомендуемый** вариант — **полный `git clone`** в выбранный каталог: совпадают пути в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml) (`./devops/postgres/...`), дальше удобнее CD (ит. 5).

**На сервере** (подставьте **свой** URL репозитория):

```bash
# при необходимости: sudo apt-get update && sudo apt-get install -y git
sudo mkdir -p /opt/llmstart
sudo chown "$USER:" /opt/llmstart
cd /opt/llmstart
# пример — SSH (удобно, если на сервере настроен deploy- или личный ключ, добавленный в GitHub):
git clone git@github.com:<OWNER>/llmstart-fullstack-live.git .
# пример — HTTPS (для приватного репо см. ниже «HTTPS + PAT»)
# git clone https://github.com/<OWNER>/llmstart-fullstack-live.git .
```

### Если `Permission denied (publickey)` при `git@github.com:…`

Сообщение значит: **на этом хосте** (у пользователя `root` или у того, под кем вы клонируете) **нет** приватного ключа, которому GitHub доверяет, либо ключ не подхватывается.

**Вариант A — HTTPS + PAT (часто быстрее всего на новом VPS)**

1. Создайте [классический PAT](https://github.com/settings/tokens) с правом **`repo`** (доступ к приватным репозиториям) — **только для клона**; срок ограничьте; **не** вставляйте токен в тикеты и issue.
2. Клонируйте по HTTPS и на запрос пароля укажите **PAT** (не пароль от аккаунта GitHub):

```bash
cd /opt/llmstart
git clone https://github.com/<OWNER>/llmstart-fullstack-live.git .
```

Логин при запросе: **ваш GitHub username**; пароль: **PAT**. Либо одной строкой (токен не попадёт в репозиторий, но может остаться в history — осторожнее):

```bash
git clone "https://<GITHUB_USERNAME>:<PAT>@github.com/<OWNER>/llmstart-fullstack-live.git" .
```

**Вариант B — отдельный SSH-ключ на сервере**

1. На **VPS** (лучше не от `root`, а от пользователя деплоя; иначе ключи в `/root/.ssh`):

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -N "" -C "vps-llmstart-clone"
cat ~/.ssh/id_ed25519_github.pub
```

2. Скопируйте **одну строку** `ssh-ed25519 …` в GitHub:
   - **репозиторий** → **Settings → Deploy keys → Add deploy key** (только чтение, если CD потом через другой механизм), **или**
   - **аккаунт** → **SSH and GPG keys** (ключ со всех репо, куда у аккаунта есть доступ).
3. Укажите Git использовать этот ключ:

```bash
printf '%s\n' \
  'Host github.com' \
  '  HostName github.com' \
  '  User git' \
  '  IdentityFile ~/.ssh/id_ed25519_github' \
  '  IdentitiesOnly yes' >> ~/.ssh/config
chmod 600 ~/.ssh/config
ssh -T git@github.com
# ожидается: Hi <user>! You've successfully authenticated…
cd /opt/llmstart
git clone git@github.com:<OWNER>/llmstart-fullstack-live.git .
```

Ключ, которым вы **подключаетесь к VPS** по SSH с ноутбука, **другой** — он в `authorized_keys` на сервере и **не** передаётся в GitHub автоматически; для `git@github.com` на сервере нужен **свой** ключ (вариант B) либо HTTPS (вариант A).

Проверка, что **корень** клона — это то место, где лежат `docker-compose.ghcr.yml` и `devops/vps/bootstrap-debian-ubuntu.sh`:

```bash
ls -la docker-compose.ghcr.yml devops/vps/bootstrap-debian-ubuntu.sh
```

**Альтернативы** (если clone пока невозможен):

- **SCP** с локальной машины: скопируйте каталог `devops/vps` или только `devops/vps/bootstrap-debian-ubuntu.sh` (см. [devops/vps/README.md](../../devops/vps/README.md)), затем перейдите к [§3](#3-установка-docker-и-утилит-bootstrap) и **потом** всё равно лучше получить полный клон для compose и `postgres` init.
- **Минимум без полного клона:** вручную доставить на сервер `docker-compose.ghcr.yml` и `devops/postgres/docker-entrypoint-initdb.d/` с **теми же** относительными путями, что в YAML — сопровождать сложнее; полный клон предпочтительнее.

## 3. Установка Docker и утилит (bootstrap)

Выполняйте **из корня** уже существующего клона (см. [§2](#2-копирование-репозитория-на-vps)):

```bash
cd /opt/llmstart   # или ваш путь к корню репозитория
chmod +x devops/vps/bootstrap-debian-ubuntu.sh
sudo ./devops/vps/bootstrap-debian-ubuntu.sh
```

Скрипт ставит **Docker Engine**, **Compose plugin** v2 (`docker compose`, нужен для `--wait` в `make stack-up-ghcr`), `git`, `curl`.  
Если вас добавили в группу `docker` — в текущей SSH-сессии выполните `newgrp docker` **или** перелогиньтесь, иначе используйте `sudo docker ...` (временно).

**UFW / firewall** скрипт **не** настраивает: см. [§7](#7-фаервол-и-доступ-снаружи).

## 4. Файлы окружения (только на сервере)

| Файл | Источник правды в репо | Что сделать |
|------|------------------------|------------|
| Корневой `.env` (рядом с `docker-compose.ghcr.yml`) | [`.env.ghcr.example`](../../.env.ghcr.example) | `LLMSTART_GHCR_IMAGE_ROOT=ghcr.io/<владелец>/<репо>` (нижний регистр), `IMAGE_TAG=latest` или `sha-…` |
| Тот же `.env` при необходимости | — | `BACKEND_API_CLIENT_TOKEN=…` — общий секрет web→backend, если задан в backend (см. [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml) у сервиса `web`) |
| `backend/.env` | [backend/.env.example](../../backend/.env.example) | Ключи LLM (`OPENROUTER_*`), `SYSTEM_PROMPT_PATH` (путь к системному промпту для LLM, по умолчанию `bot/prompts/system.txt` в [конфиге backend](../../backend/app/config.py) — **это настройка ядра**, не бота), `BACKEND_API_CLIENT_TOKEN`, `LOG_LEVEL` и т.д. **Не** кладите секреты в git. |
| `bot/.env` | [bot/.env.example](../../bot/.env.example) | `TELEGRAM_TOKEN`, при необходимости `COHORT_ID` / `MEMBERSHIP_ID`, токен к API, если backend требует Bearer. Прокси — см. [§ ниже](#пояснения-system_prompt_path-и-прокси-бота). |
| `frontend/web/.env.local` | [frontend/web/.env.example](../../frontend/web/.env.example) (только локально) | **На VPS с GHCR-стеком не копируется и не подключается:** в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml) у `web` **нет** `env_file` — только `BACKEND_ORIGIN: http://backend:8000` и `BACKEND_API_CLIENT_TOKEN` из **корневого** `.env` (см. строки таблицы выше). Сборка образа `web` — в CI ([`devops/web/Dockerfile`](../../devops/web/Dockerfile)), рантайм-контейнера читает env из compose. **Локальная** разработка веба — [onboarding.md](../onboarding.md), [docker-compose-local.md](docker-compose-local.md). |

### Пояснения: `SYSTEM_PROMPT_PATH` и прокси бота

- **`SYSTEM_PROMPT_PATH` не относится к `bot/.env`:** переменная только у **backend** ([`backend/.env.example`](../../backend/.env.example), [`config.py` — `Settings`](../../backend/app/config.py)): путь к файлу с **системным промптом для LLM** внутри контейнера backend. Бот в Telegram этот файл **не** читает. Для GHCR-деплоя укажите путь **в `backend/.env`**; чаще достаточно значения по умолчанию из примера.

- **`BACKEND_HTTP_PROXY`** (см. [`bot/.env.example`](../../bot/.env.example)) — URL HTTP(S)-прокси **только** для **HTTP-запросов бота к API backend** (httpx). Не путать с **`PROXY_URL`**: тот — для **исходящих к Telegram** (aiogram; см. [README — заметка про `PROXY_URL` / `BACKEND_HTTP_PROXY`](../../README.md)). В одном `docker compose` сеть связана напрямую: прокси к backend **обычно не нужен**; [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml) для `bot` задаёт `BACKEND_HTTP_PROXY: ""` в `environment` (перекрывает `env_file`). Указывайте `BACKEND_HTTP_PROXY` только если запросы бота к `http://backend:8000` в вашей сети **должны** идти через отдельный HTTP-прокси.

**Compose** для backend в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml) задаёт подключение к БД через `postgres:` и `DATABASE_URL`/`DOCKER_DATABASE_URL` в `environment` — согласовано с [docker-compose-ghcr.md](docker-compose-ghcr.md).

Команды копирования шаблонов **на сервере**, из **корня** клона:

```bash
cd /opt/llmstart   # корень клона
cp .env.ghcr.example .env
# отредактируйте .env (nano/vim)
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env
# отредактируйте под прод
```

## 5. Ручной `docker login ghcr.io` (выполняет владелец на сервере)

**Автоматизация в репозитории не выполняет логин** — ввод токена только на **вашей** стороне.

- Если пакеты GHCR **публичные** — **пропустите** этот шаг.
- Если **приватные** — подставьте **GitHub username** и **токен** (не коммитите, не вставляйте в тикеты):

```bash
echo '<GITHUB_TOKEN>' | docker login ghcr.io -u '<GITHUB_USERNAME>' --password-stdin
```

**Безопасность:** токен попадёт в shell history, если вводить в открытом виде в интерактивной строке; предпочтительно одноразово задать переменные в подоболочке или использовать `--password-stdin` как выше, **не** логируя токен в CI-скриптах. Не пересылайте токен в чаты.

После успешного login: `docker pull` / `docker compose pull` к образам `ghcr.io/...` должны проходить (проверка DoD).

## 6. Запуск стека

Из **корня** клона (там, где `docker-compose.ghcr.yml` и `.env`):

```bash
cd /opt/llmstart
docker compose -f docker-compose.ghcr.yml --profile app pull
docker compose -f docker-compose.ghcr.yml --profile app up -d --wait
```

Эквивалент локально: **`make stack-up-ghcr`** в [Makefile](../../Makefile) (на сервере `make` может отсутствовать — суть в двух командах выше).

Статус и логи:

```bash
docker compose -f docker-compose.ghcr.yml --profile app ps
docker compose -f docker-compose.ghcr.yml --profile app logs -f --tail=100
```

Останов:

```bash
docker compose -f docker-compose.ghcr.yml --profile app down
```

### Если `llmstart-backend` в статусе **unhealthy** / `dependency failed`

Сначала **логи** (там чаще всего видна причина):

```bash
docker logs llmstart-backend --tail 200
```

**Типовые причины:**

1. **Падение в entrypoint до uvicorn** — [docker-entrypoint.sh](../../devops/backend/docker-entrypoint.sh) выполняет `alembic upgrade head`. Ошибка миграции (структура БД, сеть до `postgres`, неверные права) останавливает контейнер: в логах будет Traceback **Alembic** / `OperationalError` / `asyncpg`.  
   - **`ModuleNotFoundError: No module named 'psycopg2'`** — в lock образа **backend** должна быть **`psycopg2-binary`**. Обновите образ из CI, снова `docker compose pull` / `up`.
   - **`FileNotFoundError: … progress-import.v1.json`** — миграция `0003` читает сид-файл: в [образе](../../devops/backend/Dockerfile) он кладётся в `/app/import-data/`; на хосте при `alembic` из корня репо путь — `data/` в **корне** клона. Обновите **backend**-образ с этим Dockerfile и `pull`, либо убедитесь, что в клоне на VPS есть [`data/progress-import.v1.json`](../../data/progress-import.v1.json).
2. **Ошибка при старте приложения** (валидация [Settings](../../backend/app/config.py), подключение к БД) — в логах **uvicorn** / Python-исключение **до** приёма запросов; healthcheck на `/health` не проходит, пока процесс не слушает `8000`.
3. **Неверный `backend/.env`** (битая строка, лишние кавычки, невалидные значения) — смотрите лог; для подключения к БД в Docker compose всё равно подставляет [переменные `DATABASE_URL` / `DOCKER_DATABASE_URL` в YAML](../../docker-compose.ghcr.yml) и [entrypoint](../../devops/backend/docker-entrypoint.sh), но ошибка в файле всё ещё может мешать загрузке env.

**Доп. проверки** (пока контейнер не в постоянном `Restarting`):

```bash
docker inspect llmstart-backend --format 'Status={{.State.Status}} Exit={{.State.ExitCode}} OOM={{.State.OOMKilled}}'
docker exec llmstart-backend /app/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read()"
# в образе backend обычно **нет** curl; проверка как в healthcheck в [docker-compose.ghcr.yml](../../docker-compose.ghcr.yml)
```

Пустой `OPENROUTER_API_KEY` **не** должен сам по себе валить `/health` (при старте подставляется заглушка LLM, см. [lifespan в `main.py`](../../backend/app/main.py)) — в первую очередь смотрите **БД и миграции** по логам.

## 7. Фаервол и доступ снаружи

Порты в [docker-compose-ghcr.md](docker-compose-ghcr.md) / YAML: **8000** (backend), **3000** (web), **5432** (Postgres; для прода **не** обязательно публиковать наружу — только если нужен доступ с хоста к БД).

Если `curl` с **самого** сервера к `127.0.0.1` работает, а с **вашего ПК** по `<PUBLIC_IP>` — нет, откройте порты в **панели облака** (Timeweb) и/или **UFW**:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

**Порядок:** не блокируйте SSH до `allow OpenSSH`. Для теста можно временно `sudo ufw disable` (только в контролируемой среде).

## 8. Проверки (API и браузер)

На **сервере**:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health
# ожидается 200
```

**Браузер** (с ПК, если открыт доступ к **PUBLIC_IP**):

- `http://<PUBLIC_IP>:8000/health` — успешный ответ HTTP (тело — как реализовано в backend).
- `http://<PUBLIC_IP>:3000` — веб.

Если внешний доступ закрыт — **SSH port forward**:  
`ssh -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 -i <ключ> <user>@<PUBLIC_IP>`  
затем на локальной машине: `http://127.0.0.1:3000` и `http://127.0.0.1:8000/health`.

## 9. Чеклист Definition of Done (итерация 4)

**Self-check (репозиторий):** скрипт и инструкция без секретов; для приватных пакетов в тексте — связка «ручной login → `compose pull` работает».

**User-check (владелец):** **git clone** на VPS → bootstrap → положить `.env` / `backend/.env` / `bot/.env` → **самостоятельно** `docker login` (если нужно) → `docker compose up` → health API и веб в браузере (или через tunnel). Понятно, что **только на сервере** / в Secrets для CD, а не в git.

## Ссылки

- [tasklist-devops — итерация 4](../tasks/tasklist-devops.md#iteration-4-server-setup)
- [docker-compose-ghcr.md](docker-compose-ghcr.md)
- [devops/vps/bootstrap-debian-ubuntu.sh](../../devops/vps/bootstrap-debian-ubuntu.sh)
