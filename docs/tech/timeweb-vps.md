# Продовый VPS в Timeweb Cloud (`twc`, SSH)

Минимальная VPS с **публичным внешним IP** и доступом по **SSH с ключом** — база для ручного деплоя ([docker-compose-ghcr.md](docker-compose-ghcr.md)) и последующего CD ([iter. 4–5 в tasklist-devops.md](../tasks/tasklist-devops.md)).

**Создание и оплата ресурса в Timeweb Cloud** выполняет **владелец** аккаунта; **агент/автоматизация** не инициирует списания и не создаёт машины без явного согласия. Ниже — воспроизводимый сценарий и политика секретов: в репозиторий **не** коммитить приватные ключи, токены API и пароли.

Политика по секретам в целом: [документация в начале tasklist-devops.md](../tasks/tasklist-devops.md) (GitHub Secrets, `.env` только вне git).

## SSH-ключи

### Рекомендация по типу

- Предпочтительно **ED25519** (короткий ключ, современные клиенты).
- **RSA** допустим, если политика команды или интеграции требуют (например `ssh-keygen -t rsa -b 4096`).

### Генерация (пример)

```bash
# Персональный ключ (ручной вход разработчика)
ssh-keygen -t ed25519 -f ~/.ssh/llmstart_dev -C "llmstart-dev@local"

# Отдельный ключ только для CI/CD (деплой; итерация 5 tasklist-devops)
ssh-keygen -t ed25519 -f ~/.ssh/llmstart_deploy -C "llmstart-deploy-gha"
```

- **Приватные** файлы (`llmstart_dev`, `llmstart_deploy` **без** `.pub`) — только на диске разработчика/в секретах CI (**GitHub Secrets**), **не** в git.
- **Публичные** (`.pub`) — в панели Timeweb при создании сервера (`--ssh-key`), в **SSH keys** личного кабинета, и/или в `~/.ssh/authorized_keys` на сервере после установки.

### Два смысла ключей


| Ключ           | Назначение                             | Где публичная часть                                                                           |
| -------------- | -------------------------------------- | --------------------------------------------------------------------------------------------- |
| Персональный   | Ручной SSH для отладки и сопровождения | Панель / `twc --ssh-key`, `authorized_keys`                                                   |
| CI/CD (deploy) | Только для автодеплоя (GitHub Actions) | Тот же механизм на сервере; **приватный** — в **Secret** репозитория (см. будущую итерацию 5) |


**Не** использовать один и тот же приватный ключ и для личного входа, и для CI: при компромисса CI проще отозвать только deploy-ключ.

### Проверка клиента SSH

```bash
ssh -i ~/.ssh/llmstart_dev <user>@<PUBLIC_IP>
```

Подставьте путь к **своему** приватному ключу, пользователя ОС (часто `root` на минимальном образе) и **публичный** IP. Значения не копируйте в репозиторий.

### Windows (пошагово, PowerShell)

1. **Убедиться, что есть OpenSSH Client.** В PowerShell: `Get-Command ssh, ssh-keygen`. Если не найдено: *Параметры → Приложения → Доп. компоненты → Добавить компонент* → **Клиент OpenSSH** (Windows 10/11), либо `winget install Microsoft.OpenSSH.Beta` (см. [документацию Microsoft](https://learn.microsoft.com/windows-server/administration/openssh/openssh_install_firstuse)).
2. **Создать каталог для ключей** (если ещё нет):
  `New-Item -ItemType Directory -Force -Path $env:USERPROFILE\.ssh`
3. **Сгенерировать персональный ключ** (в PowerShell, одна команда; пароль на ключ по желанию — можно Enter для пустого, но для прод лучше задать):
  `ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\llmstart_dev" -C "llmstart-dev@local"`
4. **Сгенерировать deploy-ключ отдельно:**
  `ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\llmstart_deploy" -C "llmstart-deploy-gha"`
5. **Что лежит на диске:** рядом с `llmstart_dev` появятся `llmstart_dev` (приватный) и `llmstart_dev.pub` (публичный). То же для `llmstart_deploy`. **В git коммитить только в игнорируемых/личных сценариях** — в репозиторий проекта ключи **не** добавлять; при необходимости добавьте `*.pub` / приватные имена в свой глобальный `.gitignore`, если храните ключи внутри клонов.
6. **Скопировать публичный ключ в буфер** (для вставки в панель Timeweb / на сервер):
  `Get-Content -Raw $env:USERPROFILE\.ssh\llmstart_dev.pub | Set-Clipboard`  
   Либо откройте `notepad $env:USERPROFILE\.ssh\llmstart_dev.pub` и скопируйте одну строку, начинающуюся с `ssh-ed25519`.
7. **Первый вход на VPS** (подставьте IP с панели Timeweb):
  `ssh -i $env:USERPROFILE\.ssh\llmstart_dev root@<PUBLIC_IP>`
8. **WSL:** если генерируете ключи *внутри* Linux (WSL), пути будут `~/.ssh/...` в файловой системе WSL — это **другой** набор файлов, не `C:\Users\...`. Для `twc` в Windows и `ssh` в PowerShell удобнее хранить ключи в `C:\Users\<вы>\.ssh\` и в `twc` указывать публичный ключ как `C:\Users\<вы>\.ssh\llmstart_dev.pub` (или путь в кавычках).
9. **Если `ssh` ругается на права на приватный ключ** (unprotected private key; часто после копирования с флешки), в **PowerShell от имени администратора** последовательно:
  `icacls $env:USERPROFILE\.ssh\llmstart_dev /inheritance:r`  
   `icacls $env:USERPROFILE\.ssh\llmstart_dev /grant:r "$($env:USERNAME):R"`

## CLI `twc`

Официальное руководство (RU): [twc — README](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md).

### Установка (кратко, любая ОС)

- Рекомендуется: `pip install twc-cli` (нужен Python ≥ 3.8) или `pipx install twc-cli` — см. [раздел «Установка»](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md#установка) в README `twc`.
- **Linux / macOS:** в примерах ниже публичный ключ удобно указывать как `~/.ssh/llmstart_dev.pub`.

### Windows (пошагово, PowerShell)

Один сценарий: установить `twc`, залогиниться токеном, выбрать пресет и образ, вызвать `twc server create` с **Windows-путём** к `*.pub`. **Команда `twc server create` заказывает платный ресурс** — согласуйте регион, пресет и цену **до** запуска.

#### 1) Python

- Установите [Python для Windows](https://www.python.org/downloads/windows/) (3.10+), в инсталляторе включите **Add python.exe to PATH**.
- Новый PowerShell: `py -3 --version` (или `python --version`).

#### 2) Пакет `twc-cli`

```powershell
py -3 -m pip install --user --upgrade pip
py -3 -m pip install --user twc-cli
```

- Закройте и снова откройте терминал, затем: `Get-Command twc`.  
- Если `twc` не находится, добавьте в **PATH** пользователя каталог `Scripts` (часто `%APPDATA%\Python\Python3x\Scripts` — см. `py -0p` / доку Python), либо используйте `py -3 -m twc --help`, если модульный запуск у вашей установки есть.

**Вариант [pipx](https://pypa.github.io/pipx/):** `py -3 -m pip install --user pipx`, `py -3 -m pipx ensurepath`, перезапуск сессии, `pipx install twc-cli`.

#### 3) Токен API (не класть в git)

1. В браузере: [Токены API](https://timeweb.cloud/my/api-keys) в Timeweb Cloud — создайте токен, **один раз** скопируйте.
2. PowerShell: `twc config` — вставьте токен (в **Windows Terminal** чаще **Ctrl+Shift+V** или ПКМ). Где лежит конфиг — [«Конфигурация»](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md#конфигурация) в README `twc`.
3. Проверка: `twc project list` или `twc server list` без ошибки авторизации.

#### 4) Путь к персональному `*.pub`

```powershell
$pub = Join-Path $env:USERPROFILE ".ssh\llmstart_dev.pub"
Test-Path $pub   # True, если ключ уже создан
```

#### 5) Пресет и образ

```powershell
twc server list-presets -f location:ru-1,disk_type:nvme
twc server list-os-images
```

Запишите `**preset_id**` и строку **образа** вроде `ubuntu-24.04` (см. [создание сервера](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md#создание-сервера) в `twc`).

#### 6) Создать сервер

Подставьте свои `имя`, `образ`, `id` пресета:

```powershell
twc server create --name "llmstart-prod" --image <образ> --preset-id <id> --ssh-key $pub
```

Или явный путь в кавычках:

```powershell
twc server create --name "llmstart-prod" --image ubuntu-24.04 --preset-id 2449 --ssh-key "C:\Users\apfisenko\.ssh\llmstart_dev.pub"
```

Альтернатива — конфигурация по частям: `--cpu`, `--ram`, `--disk`, `--region` — без `--preset-id`, [по доке](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md#создание-сервера) `twc`.

#### 7) IP и состояние

`twc server list` и `twc server get <id_сервера>` — публичный **IPv4** в блоке сети. Дополнительно сверяйтесь с веб-панелью.

#### 8) Ключи и `twc`

Повторно регистрировать тот же публичный ключ в панели не требуется, если `twc` принимает уже зарегистрированное имя/ID (см. upstream README про `--ssh-key`).

#### 9) Второй ключ (CI) на существующем сервере

1. `Get-Content -Raw $env:USERPROFILE\.ssh\llmstart_deploy.pub | Set-Clipboard` — **публичная** строка.
2. `ssh -i $env:USERPROFILE\.ssh\llmstart_dev root@<PUBLIC_IP>` — зайдите **персональным** ключом.
3. На Linux: добавьте строку в `~/.ssh/authorized_keys` (права `700` на каталог, `600` на файл) **или** используйте панель Timeweb.
4. **Приватный** `llmstart_deploy` позже — только в **GitHub Secrets** репозитория ([итерация 5 tasklist-devops](../tasks/tasklist-devops.md#iteration-5-cd-gha)), не в git.



### **Зачем это**

Чтобы **вход по SSH** работал, на сервере в домашней папке пользователя (у `root` это `/root`) в файле `~/.ssh/authorized_keys` лежат **строки публичных** ключей (по одной на строку).  
Типичная ошибка: неверные **права** на `~/.ssh` или `authorized_keys` — тогда `sshd` **игнорирует** ключи.

---

### **Когда «добавить строку в authorized_keys»**

Имеется в виду: у вас уже есть **текст публичного** ключа (одна длинная строка из `*.pub` вида `ssh-ed25519 AAAA... comment`). Его нужно **добавить на сервер** — либо вручную в файл, либо через панель, если она умеет «SSH keys».

---

### **Вариант A: вы уже залогинились (например под** `root` **по рабочему ключу)**

1. **Проверьте**, что папка и файл согласованы:
  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  touch ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
2. **Добавьте строку ключа** (лучше не копировать с телефона — одна длинная строка без переносов):
  - Через редактор, например:
    nano ~/.ssh/authorized_keys
    Вставьте **одну** строку из `llmstart_deploy.pub` (или другого `*.pub`), **сохраните**, выйдите.
  - Или **одной командой** (если строку аккуратно вставляете):
    echo "ssh-ed25519 AAAA...ваша_строка... deploy@pc" >> ~/.ssh/authorized_keys
    Осторожно: лишние кавычки/пробелы/две строки в одной — ломают запись. Для `echo` проще, если ключ **во временной переменной** или вставка через `nano`.
3. **Снова права (на всякий случай):**
  chmod 700 ~/.ssh
  chmod 600 ~/.ssh/authorized_keys
  chown -R root:root ~/.ssh
  (если настраивали **не** `root` — `chown` на того пользователя, чей `~`).
4. **Перезагрузка** `sshd` **обычно не нужна**; если меняли только файл — сразу можно пробовать второй сессией `ssh` с **новым** ключом (не закрывайте текущую, пока не убедитесь, что новый вход работает).

**Права, которые ждет OpenSSH (типично):**


| **Путь**                      | **Права**                                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `~/.ssh`                      | `700` (`drwx------`)                                                                                                                              |
| `~/.ssh/authorized_keys`      | `600` (`-rw-------`)                                                                                                                              |
| Домашний каталог пользователя | у `root` обычно `0700` или `0755` — важно, чтобы «чужие» не могли писать в `~` (если `~` слишком открыт, иногда вход блокируется — у `root` реже) |


---

### **Вариант B: вы не можете зайти на сервер, но есть другой рабочий способ (консоль Timeweb)**

1. В панели **Timeweb Cloud** откройте сервер.
2. Найдите **VNC / консоль** / **экстренный доступ к терминалу** (названия зависят от панели) — зайдите **как в «локальную» сессию**, без SSH, если веб-консоль логинит **root** или даст одноразовый пароль.
3. Уже **в той** оболочке сделайте шаги из варианта A (создать `~/.ssh/authorized_keys`, вставить строку, `chmod`).

---

### **Вариант C: панель Timeweb — «SSH keys» (без ручного** `nano`**)**

Где-то в карточке **сервер** → раздел **SSH** / **Ключи** (управление ключами, которые подставляются **при провижининге** или **добавляются** на существующий сервер). Там:

1. **Добавьте** публичный ключ (текст из `файл.pub`) **или** выберите уже сохранённый в аккаунте.
2. Укажите, что ключ должен применяться **к этому** серверу (если панель спрашивает).

**Важно:** в разных панелях: ключ мог быть учтён **только при создании** ВМ, а **после** — только через VNC/ручной `authorized_keys` или отдельное действие «добавить ключ». Если кнопки нет — используйте варианты A/B.

---

### **Как не накосячить**

- В `authorized_keys` **одна** строка = **один** ключ, **без** обрывов на две строки.
- **Не** кладите **приватный** ключ на сервер (тот **без** `.pub`); в `authorized_keys` — **только публичный** (`*.pub`).
- После правок **проверьте новую сессию** (второй терминал), **не** выкидывайте старую, пока не убедились, что вход с новым ключом работает.

---

### **С Windows: откуда взять «строку»**

На своём ПК (PowerShell):

Get-Content -Raw $env:USERPROFILE\.ssh\llmstart_deploy.pub

Скопируйте **целиком одну** строку и вставьте на сервере в `authorized_keys` (как в варианте A) **или** в панель Timeweb, если она просит «публичный ключ».

---

Итог: **добавить в** `~/.ssh/authorized_keys` **публичную строку, выставить** `700` **и** `600`**,** при отсутствии SSH сначала **консоль Timeweb** или **панель** для привязки ключа, если она у вас это поддерживает.

### Создание сервера (сводка, Linux / macOS)

```bash
twc server create --name <имя> --image <образ> --preset-id <id> --ssh-key ~/.ssh/llmstart_dev.pub
```

Далее: `twc server list` / `twc server get <id>`. Актуальные флаги — [README `twc](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md#создание-сервера)`.

## Минимальная конфигурация под стек LLMStart

Критерий: **внешний IP**, **SSH по ключу**, достаточно **RAM/CPU/диска** для контейнеров из `[docker-compose.ghcr.yml](../../docker-compose.ghcr.yml)`: **PostgreSQL** + **backend** + **web** + **bot** (четыре сервиса приложения плюс БД; точные лимиты зависят от нагрузки).

Ориентир: не ниже **~2 vCPU** и **~4 GiB RAM** для комфортного старта полного стека; диск **≥ 30–50 GiB** под образы и данные БД. Конкретный пресет и регион выбирает владелец по цене и требованиям; артикул в документации **не** фиксируем — используйте `twc server list-presets` на дату развёртывания.

## Запись об инстансе (без секретов)

Зафиксируйте идентификацию **в личных заметках** или в защищённом Confluence/Notion. В **git** помещайте **только** то, что явно согласовано политикой (часто **публичный IP** и имя в облаке **не** считаются секретом, но это решение **команды**). **Никогда** не хранить в репозитории: приватные ключи, токены API, root-пароль из ответа API, если он когда-либо отображается.

Шаблон (скопируйте и заполните **вне** git, если сомневаетесь):


| Поле                                      | Пример / placeholder                 |
| ----------------------------------------- | ------------------------------------ |
| Имя в Timeweb                             | `llmstart-prod`                      |
| ID сервера (из `twc server list` / панели | 7677937                              |
| Регион / локация                          | `ru-1`                               |
| ОС (образ)                                | `ubuntu-24.04`                       |
| Публичный IPv4                            | 91.210.168.20                        |
| Примечание                                | firewall, бэкапы — по мере настройки |


## Проверки (чеклист)

1. **Персональный ключ:** `ssh -i <приватный_персональный> <user>@<PUBLIC_IP>` — успешный вход, без ввода пароля (при настроенном ключе).
2. **Ключ CI/CD:** сгенерирован отдельно; публичная часть есть на сервере. Полная проверка `ssh` из **GitHub Actions** — в [итерациях 4–5](../tasks/tasklist-devops.md) (когда в Secrets добавлен private key и известен пользователь/хост).
3. **twc:** `twc server list` показывает сервер, статус `on`, в выводе виден ожидаемый **публичный** IP.

## Дальше

- Полная пошаговая инструкция: [vps-manual-ghcr-deploy.md](vps-manual-ghcr-deploy.md) (**сначала** `git clone` на VPS, затем bootstrap Docker, `.env`, **ручной** `docker login ghcr.io`, `docker compose`, фаервол, проверки). Обзор образов: [docker-compose-ghcr.md](docker-compose-ghcr.md), статус в [iter. 4 в tasklist-devops.md](../tasks/tasklist-devops.md#iteration-4-server-setup).
- **Deploy-ключ** для GitHub: приватный только в **Secrets**; имена переменных — в документации [итерации 5 (CD)](../tasks/tasklist-devops.md#iteration-5-cd-gha).

## Ссылки

- [tasklist-devops — итерация 3](../tasks/tasklist-devops.md#iteration-3-timeweb-vps)
- [twc — пользовательское руководство (RU, GitHub)](https://raw.githubusercontent.com/timeweb-cloud/twc/refs/heads/master/docs/ru/README.md)
- [Стек из образов GHCR](docker-compose-ghcr.md)

