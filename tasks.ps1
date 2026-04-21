#requires -Version 5.1
<#
.SYNOPSIS
  Makefile-like tasks for Windows PowerShell (dev, DB, tests).

.DESCRIPTION
  Run from repo root: .\tasks.ps1 install | db-up | db-status | db-migrate | test-backend ...

  Если в PowerShell нет `docker` в PATH, скрипт сам использует `wsl -e docker compose`
  (Docker только внутри WSL). Иначе можно задать вручную:
    $env:DOCKER_COMPOSE = "wsl -d Ubuntu -e docker compose"; .\tasks.ps1 db-up

  Env vars (same as Makefile): POSTGRES_*, DATABASE_URL, TEST_DATABASE_URL, DOCKER_COMPOSE, STACK_SERVICE (для stack-logs).
#>
param(
    [Parameter(Position = 0)]
    [string] $Task = "help"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot

if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = "llmstart" }
if (-not $env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD = "llmstart" }
if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = "llmstart" }
if (-not $env:POSTGRES_TEST_DB) { $env:POSTGRES_TEST_DB = "llmstart_test" }
$pgUrlDefault = "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_DB)"
$pgTestDefault = "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_TEST_DB)"
if (-not $env:DATABASE_URL) { $env:DATABASE_URL = $pgUrlDefault }
if (-not $env:TEST_DATABASE_URL) { $env:TEST_DATABASE_URL = $pgTestDefault }

function Get-DockerComposeCommandPrefix {
    $explicit = $env:DOCKER_COMPOSE
    if ($explicit -and $explicit.Trim()) {
        return $explicit.Trim()
    }
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        return "docker compose"
    }
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        return "wsl -e docker compose"
    }
    throw (
        "docker not in PATH and wsl not found. Install Docker+WSL2 or set DOCKER_COMPOSE. " +
        'Example: $env:DOCKER_COMPOSE = "wsl -e docker compose"; .\tasks.ps1 db-up'
    )
}

function Invoke-DockerCompose {
    param([string[]] $ArgumentList)
    $prefix = Get-DockerComposeCommandPrefix
    $head = $prefix -split "\s+"
    if ($head.Count -eq 0) { throw "DOCKER_COMPOSE is empty" }
    $exe = $head[0]
    $rest = @()
    if ($head.Count -gt 1) {
        $rest = $head[1..($head.Length - 1)]
    }
    & $exe @($rest + $ArgumentList)
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
        exit $LASTEXITCODE
    }
}

function Get-RepoRootWslPath {
    # wslpath из PowerShell ломается на путях с кириллицей (кодировка аргумента). Для вида X:\... строим /mnt/x/... сами.
    $p = ($RepoRoot.TrimEnd('\', '/'))
    if ($p -match '^([A-Za-z]):[/\\](.+)$') {
        $drive = $Matches[1].ToLowerInvariant()
        $tail = ($Matches[2] -replace '\\', '/').Trim('/')
        if ($tail.Length -gt 0) {
            return "/mnt/$drive/$tail"
        }
        return "/mnt/$drive"
    }
    if ($p -match '^([A-Za-z]):$') {
        return "/mnt/$($Matches[1].ToLowerInvariant())"
    }
    $out = (& wsl wslpath -a $RepoRoot 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($out)) {
        return $out
    }
    throw (
        "Не удалось преобразовать путь репозитория для WSL: $RepoRoot " +
        "(ожидался путь вида D:\... или UNC). Запущен ли WSL?"
    )
}

function Invoke-DockerComposeWsl {
    param([string[]] $ArgumentList)
    if ($ArgumentList.Count -lt 1) {
        throw "Invoke-DockerComposeWsl: укажите аргументы compose (например stop, down)"
    }
    $wslRoot = Get-RepoRootWslPath
    # Один аргумент, чтобы путь с пробелами/Unicode не разъезжался у wsl.exe.
    & wsl -e docker compose "--project-directory=$wslRoot" @ArgumentList
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
        exit $LASTEXITCODE
    }
}

function Get-PostgresDatabaseUrl {
    return "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_DB)"
}

function Get-BackendEnvDatabaseUrlLine {
    $path = Join-Path $RepoRoot "backend\.env"
    if (-not (Test-Path -LiteralPath $path)) {
        return $null
    }
    foreach ($line in Get-Content -LiteralPath $path) {
        if ($line -match '^\s*DATABASE_URL\s*=\s*(.+)\s*$') {
            return $matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $null
}

function Parse-DatabaseUrlTcpTarget {
    param([string] $Url)
    $hostOut = "127.0.0.1"
    $portOut = 5432
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return @{ Host = $hostOut; Port = $portOut }
    }
    $idx = $Url.LastIndexOf('@')
    if ($idx -lt 0) {
        return @{ Host = $hostOut; Port = $portOut }
    }
    $afterAt = $Url.Substring($idx + 1)
    $slashIdx = $afterAt.IndexOf('/')
    if ($slashIdx -ge 0) {
        $afterAt = $afterAt.Substring(0, $slashIdx)
    }
    $hostPart = $afterAt
    if ($afterAt.Contains(':')) {
        $lastColon = $afterAt.LastIndexOf(':')
        $hostPart = $afterAt.Substring(0, $lastColon)
        $portStr = $afterAt.Substring($lastColon + 1)
        if ($portStr -match '^\d+$') {
            $portOut = [int]$portStr
        }
    }
    $h = $hostPart.Trim().ToLowerInvariant()
    if ($h -eq "localhost" -or $h -eq "::1") {
        $hostOut = "127.0.0.1"
    }
    else {
        $hostOut = $hostPart.Trim()
    }
    return @{ Host = $hostOut; Port = $portOut }
}

function Get-PostgresTcpTargetForDev {
    $fromFile = Get-BackendEnvDatabaseUrlLine
    return (Parse-DatabaseUrlTcpTarget -Url $fromFile)
}

function Test-PostgresTcp {
    param(
        [string] $ComputerName,
        [int] $Port
    )
    $tcp = $null
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($ComputerName, $Port)
        return ($tcp.Connected)
    }
    catch {
        return $false
    }
    finally {
        if ($null -ne $tcp) {
            $tcp.Close()
        }
    }
}

function Wait-PostgresPort {
    param(
        [string] $ComputerName = "127.0.0.1",
        [int] $Port = 5432,
        [int] $TimeoutSec = 90
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if (Test-PostgresTcp -ComputerName $ComputerName -Port $Port) {
            return
        }
        Start-Sleep -Milliseconds 300
    }
    throw @"
PostgreSQL не принимает TCP на ${ComputerName}:${Port} за $TimeoutSec с.

Проверьте по шагам:
  1) Запущен ли Docker (Docker Desktop) и контейнер: из корня репозитория — .\tasks.ps1 db-up (или docker compose up -d --wait postgres).
  2) Порт $Port не занят другим Postgres на хосте: netstat -ano | findstr :$Port
  3) Если docker только в WSL: `$env:DOCKER_COMPOSE = 'wsl -e docker compose'; .\tasks.ps1 db-up`
  4) backend/.env — DATABASE_URL с хостом 127.0.0.1 и тем же портом, что проброшен из compose (по умолчанию 5432).
"@
}

function Invoke-Backend {
    param([string[]] $ArgumentList)
    if ($ArgumentList.Count -lt 1) {
        throw "Invoke-Backend: empty command"
    }
    $cmd = $ArgumentList[0]
    $cmdArgs = @()
    if ($ArgumentList.Count -gt 1) {
        $cmdArgs = $ArgumentList[1..($ArgumentList.Count - 1)]
    }
    Push-Location (Join-Path $RepoRoot "backend")
    try {
        & $cmd @cmdArgs
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

function Task-Install {
    uv sync --group dev
    Invoke-Backend @("uv", "sync", "--extra", "dev")
}

function Task-BotDev {
    uv run python -m bot.main
}

function Task-Lint {
    uv run ruff check bot
    uv run ruff format --check bot
    # backend: ruff только в optional-dependencies dev — нужен --extra dev, иначе «Failed to spawn: ruff»
    Invoke-Backend @("uv", "run", "--extra", "dev", "ruff", "check", "app", "tests")
    Invoke-Backend @("uv", "run", "--extra", "dev", "ruff", "format", "--check", "app", "tests")
}

function Task-Format {
    uv run ruff format bot
    uv run ruff check --fix bot
    Invoke-Backend @("uv", "run", "--extra", "dev", "ruff", "format", "app", "tests")
    Invoke-Backend @("uv", "run", "--extra", "dev", "ruff", "check", "--fix", "app", "tests")
}

function Task-TestBackend {
    Invoke-Backend @("uv", "sync", "--extra", "dev")
    Invoke-Backend @("uv", "run", "pytest", "tests/pg")
}

function Task-DbTestCreate {
    $db = $env:POSTGRES_TEST_DB
    $prefix = Get-DockerComposeCommandPrefix
    $head = $prefix -split "\s+"
    $exe = $head[0]
    $rest = @()
    if ($head.Count -gt 1) {
        $rest = $head[1..($head.Length - 1)]
    }
    $psqlBase = $rest + @(
        "exec", "-T", "-e", "PGPASSWORD=$($env:POSTGRES_PASSWORD)", "postgres",
        "psql", "-U", $env:POSTGRES_USER, "-d", "postgres"
    )
    $check = & $exe @($psqlBase + @("-tc", "SELECT 1 FROM pg_database WHERE datname='$db'"))
    # @(...) — всегда массив (StrictMode: у скаляра нет .Count; пустой pipeline → 0 элементов).
    $exists = (@($check | Where-Object { $_ -match "^\s*1\s*$" })).Count -gt 0
    if (-not $exists) {
        & $exe @($psqlBase + @("-c", "CREATE DATABASE $db OWNER $($env:POSTGRES_USER);"))
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            exit $LASTEXITCODE
        }
    }
}

function Task-BackendDev {
    if (-not $env:LLMSTART_SKIP_POSTGRES_WAIT) {
        try {
            $pg = Get-PostgresTcpTargetForDev
            Write-Host (
                "Ожидание TCP PostgreSQL $($pg.Host):$($pg.Port) (из backend/.env DATABASE_URL; таймаут как у db-up, 90 с)..."
            ) -ForegroundColor DarkGray
            Wait-PostgresPort -ComputerName $pg.Host -Port $pg.Port -TimeoutSec 90
        }
        catch {
            Write-Host $_.Exception.Message -ForegroundColor Red
            Write-Host "Чтобы запустить uvicorn без этой проверки (удалённый Postgres и т.д.): `$env:LLMSTART_SKIP_POSTGRES_WAIT=1" -ForegroundColor Yellow
            exit 1
        }
    }
    Invoke-Backend @("uv", "sync")
    Invoke-Backend @("uv", "run", "uvicorn", "app.main:app", "--reload")
}

function Task-BackendTypecheck {
    Write-Host "backend-typecheck: mypy is not configured; use: .\tasks.ps1 lint"
}

function Task-DbMigrate {
    $saved = $env:DATABASE_URL
    try {
        $env:DATABASE_URL = Get-PostgresDatabaseUrl
        Invoke-Backend @("uv", "sync", "--extra", "dev")
        Invoke-Backend @("uv", "run", "--no-env-file", "alembic", "upgrade", "head")
    }
    finally {
        $env:DATABASE_URL = $saved
    }
}

function Task-DbMigrateTestDb {
    $saved = $env:DATABASE_URL
    try {
        $env:DATABASE_URL = "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_TEST_DB)"
        Invoke-Backend @("uv", "sync", "--extra", "dev")
        Invoke-Backend @("uv", "run", "--no-env-file", "alembic", "upgrade", "head")
    }
    finally {
        $env:DATABASE_URL = $saved
    }
}

function Task-DbMigrateAll {
    Task-DbMigrate
    Task-DbTestCreate
    Task-DbMigrateTestDb
}

function Task-DbUp {
    Invoke-DockerCompose @("up", "-d", "--wait", "postgres")
    Wait-PostgresPort
    Task-DbMigrateAll
}

function Task-DbUpWsl {
    Invoke-DockerComposeWsl @("up", "-d", "--wait", "postgres")
    Wait-PostgresPort
    Task-DbMigrateAll
}

function Task-DbDown {
    Invoke-DockerCompose @("down")
}

function Task-DbStopWsl {
    Invoke-DockerComposeWsl @("stop")
}

function Task-DbDownWsl {
    Invoke-DockerComposeWsl @("down")
}

function Task-DbReset {
    Invoke-DockerCompose @("down", "-v")
    Invoke-DockerCompose @("up", "-d", "--wait", "postgres")
    Wait-PostgresPort
    Task-DbMigrateAll
}

function Task-DbMigrateTest {
    Task-DbMigrateAll
    Task-TestBackend
}

function Task-DbShell {
    Invoke-DockerCompose @(
        "exec",
        "-e", "PGPASSWORD=$($env:POSTGRES_PASSWORD)",
        "postgres",
        "psql", "-U", $env:POSTGRES_USER, "-d", $env:POSTGRES_DB
    )
}

function Task-DbStatus {
    Write-Host "=== docker compose ps (postgres) ===" -ForegroundColor Cyan
    Invoke-DockerCompose @("ps", "-a", "--format", "table")
    Write-Host ""
    $pg = Get-PostgresTcpTargetForDev
    Write-Host "=== TCP $($pg.Host):$($pg.Port) (как в backend/.env DATABASE_URL) ===" -ForegroundColor Cyan
    if (Test-PostgresTcp -ComputerName $pg.Host -Port $pg.Port) {
        Write-Host "OK: порт доступен (что-то слушает)." -ForegroundColor Green
    }
    else {
        Write-Host "FAIL: порт $($pg.Host):$($pg.Port) недоступен." -ForegroundColor Red
        Write-Host "Если контейнер не запущен: .\tasks.ps1 db-up" -ForegroundColor Yellow
    }
}

function Assert-PnpmInPath {
    if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
        throw "pnpm не найден в PATH. Установите Node.js LTS и включите pnpm (например corepack enable pnpm)."
    }
}

function Invoke-FrontendWebPnpm {
    param([string[]] $PnpmArgs)
    Assert-PnpmInPath
    $web = Join-Path $RepoRoot "frontend\web"
    if (-not (Test-Path -LiteralPath $web)) {
        throw "Каталог не найден: $web"
    }
    Push-Location $web
    try {
        & pnpm @PnpmArgs
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

function Task-FrontendInstall {
    Invoke-FrontendWebPnpm @("install")
}

function Task-FrontendDev {
    Invoke-FrontendWebPnpm @("dev")
}

function Task-FrontendLint {
    Invoke-FrontendWebPnpm @("lint")
}

function Task-FrontendBuild {
    Invoke-FrontendWebPnpm @("build")
}

function Task-CiCheck {
    Task-Lint
    Task-FrontendLint
    Task-FrontendBuild
}

function Task-StackUp {
    Invoke-DockerCompose @("--profile", "app", "up", "-d", "--wait")
}

function Task-StackUpWsl {
    Invoke-DockerComposeWsl @("--profile", "app", "up", "-d", "--wait")
}

function Task-StackUpGhcr {
    Invoke-DockerCompose @("-f", "docker-compose.ghcr.yml", "--profile", "app", "up", "-d", "--wait")
}

function Task-StackUpGhcrWsl {
    Invoke-DockerComposeWsl @("-f", "docker-compose.ghcr.yml", "--profile", "app", "up", "-d", "--wait")
}

function Task-StackDown {
    Invoke-DockerCompose @("--profile", "app", "down")
}

function Task-StackDownWsl {
    Invoke-DockerComposeWsl @("--profile", "app", "down")
}

function Task-StackDownGhcr {
    Invoke-DockerCompose @("-f", "docker-compose.ghcr.yml", "--profile", "app", "down")
}

function Task-StackDownGhcrWsl {
    Invoke-DockerComposeWsl @("-f", "docker-compose.ghcr.yml", "--profile", "app", "down")
}

function Task-StackStatus {
    Invoke-DockerCompose @("ps", "-a")
}

function Task-StackLogs {
    $svc = $env:STACK_SERVICE
    if ($svc -and $svc.Trim()) {
        Invoke-DockerCompose @("--profile", "app", "logs", "-f", $svc.Trim())
    }
    else {
        Invoke-DockerCompose @("--profile", "app", "logs", "-f")
    }
}

function Task-StackBuild {
    Invoke-DockerCompose @("--profile", "app", "build")
}

function Task-StackRebuildBackendWsl {
    Write-Host "WSL: docker compose --profile app down" -ForegroundColor Cyan
    Invoke-DockerComposeWsl @("--profile", "app", "down")
    Write-Host "WSL: docker compose --profile app build backend --no-cache" -ForegroundColor Cyan
    Invoke-DockerComposeWsl @("--profile", "app", "build", "backend", "--no-cache")
    Write-Host "Готово. Подъём: .\tasks.ps1 stack-up-wsl" -ForegroundColor Green
}

function Task-CheckBackend {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
        Write-Host "OK: GET http://127.0.0.1:8000/health" -ForegroundColor Green
    }
    else {
        throw "Unexpected status: $($r.StatusCode)"
    }
}

function Task-CheckWeb {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:3000/" -UseBasicParsing -TimeoutSec 10
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) {
        Write-Host "OK: GET http://127.0.0.1:3000/" -ForegroundColor Green
    }
    else {
        throw "Unexpected status: $($r.StatusCode)"
    }
}

function Task-CheckBot {
    Invoke-DockerCompose @("--profile", "app", "exec", "-T", "bot", "python", "-c", "import urllib.request; urllib.request.urlopen('http://backend:8000/health', timeout=5)")
    Write-Host "OK: bot container -> backend /health" -ForegroundColor Green
}

function Show-Help {
    # Без @" "@: в Windows PowerShell 5.1 обратные кавычки/`$ внутри расширяемой here-string ломают разбор.
    @(
        'Usage: .\tasks.ps1 <target>'
        ''
        '  install                 uv sync (repo root + backend)'
        '  bot-dev                 бот: uv run python -m bot.main (секреты в bot/.env; шаблон bot/.env.example)'
        '  ci-check                ruff + frontend-lint + frontend-build (статика как в CI; нужен frontend-install)'
        '  lint, backend-lint      ruff (bot + backend)'
        '  format                  ruff format + fix'
        '  test, test-backend, backend-test, test-all'
        '                          pytest tests/pg (PostgreSQL)'
        '  backend-dev             uvicorn --reload (ждёт TCP из backend/.env; см. LLMSTART_SKIP_POSTGRES_WAIT)'
        '  backend-typecheck       note about mypy'
        '  db-up, db-down          только сервис postgres + миграции на llmstart и llmstart_test с хоста'
        '  db-up-wsl               compose up -d --wait postgres через WSL, затем миграции (как db-up)'
        '  db-stop-wsl             compose stop через WSL (--project-directory → /mnt/... )'
        '  db-down-wsl             compose down через WSL (без -v; тома сохраняются как у db-down)'
        '  db-status               docker compose ps + TCP (хост/порт из backend/.env DATABASE_URL)'
        '  db-reset                down -v, up postgres --wait, миграции на обе БД'
        '  stack-up, stack-down    полный стек Docker (профиль app: backend, web, bot)'
        '  stack-up-wsl, stack-down-wsl — то же через WSL (--project-directory → /mnt/... )'
        '  stack-up-ghcr, stack-down-ghcr — стек из образов GHCR (-f docker-compose.ghcr.yml; LLMSTART_GHCR_IMAGE_ROOT в .env)'
        '  stack-up-ghcr-wsl, stack-down-ghcr-wsl — то же через WSL (см. docs/tech/docker-compose-ghcr.md)'
        '  stack-status            docker compose ps -a'
        '  stack-logs              docker compose logs -f (опционально $env:STACK_SERVICE=web|backend|bot|postgres)'
        '  stack-build             docker compose build --profile app'
        '  stack-rebuild-backend-wsl  compose down + build backend --no-cache через WSL (/mnt/... )'
        '  check-backend           Invoke-WebRequest http://127.0.0.1:8000/health'
        '  check-web               Invoke-WebRequest http://127.0.0.1:3000/'
        '  check-bot               exec в контейнере bot: HTTP к backend /health (нужен stack-up)'
        '  db-migrate, migrate-backend'
        '                          только llmstart: uv sync --extra dev; alembic upgrade head'
        '  db-migrate-test-db      только POSTGRES_TEST_DB (Alembic)'
        '  db-migrate-all          db-migrate + db-test-create + db-migrate-test-db'
        '                          (Alembic 0007: демо-когорта demo_frontend_mvp, akozhin / 162684825)'
        '  db-test-create          CREATE llmstart_test if missing (pytest DB)'
        '  db-migrate-test, migrate-backend-test'
        '                          db-migrate-all + pytest tests/pg'
        '  db-shell                psql in postgres container'
        '  frontend-install        pnpm install в frontend/web'
        '  frontend-dev            pnpm dev (Next.js)'
        '  frontend-lint           pnpm lint'
        '  frontend-build          pnpm build'
        ''
        'Env: DOCKER_COMPOSE, STACK_SERVICE (для stack-logs — имя сервиса), POSTGRES_*, POSTGRES_TEST_DB, DATABASE_URL, TEST_DATABASE_URL.'
        ''
        'Docker только в WSL: если `docker` не в PATH Windows, скрипт вызывает `wsl -e docker compose`.'
        'Свой дистрибутив: $env:DOCKER_COMPOSE = ''wsl -d Ubuntu -e docker compose'''
    ) | ForEach-Object { Write-Host $_ }
}

switch -Regex ($Task.ToLowerInvariant()) {
    "^(install)$" { Task-Install }
    "^(bot-dev)$" { Task-BotDev }
    "^(ci-check)$" { Task-CiCheck }
    "^(lint|backend-lint)$" { Task-Lint }
    "^(format)$" { Task-Format }
    "^(test|test-backend|backend-test|test-all)$" { Task-TestBackend }
    "^(backend-dev)$" { Task-BackendDev }
    "^(backend-typecheck)$" { Task-BackendTypecheck }
    "^(db-up)$" { Task-DbUp }
    "^(db-up-wsl)$" { Task-DbUpWsl }
    "^(db-down)$" { Task-DbDown }
    "^(db-stop-wsl)$" { Task-DbStopWsl }
    "^(db-down-wsl)$" { Task-DbDownWsl }
    "^(db-migrate|migrate-backend)$" { Task-DbMigrate }
    "^(db-migrate-test-db)$" { Task-DbMigrateTestDb }
    "^(db-migrate-all)$" { Task-DbMigrateAll }
    "^(db-reset)$" { Task-DbReset }
    "^(db-test-create)$" { Task-DbTestCreate }
    "^(db-migrate-test|migrate-backend-test)$" { Task-DbMigrateTest }
    "^(db-shell)$" { Task-DbShell }
    "^(db-status)$" { Task-DbStatus }
    "^(stack-up)$" { Task-StackUp }
    "^(stack-up-wsl)$" { Task-StackUpWsl }
    "^(stack-up-ghcr)$" { Task-StackUpGhcr }
    "^(stack-up-ghcr-wsl)$" { Task-StackUpGhcrWsl }
    "^(stack-down)$" { Task-StackDown }
    "^(stack-down-wsl)$" { Task-StackDownWsl }
    "^(stack-down-ghcr)$" { Task-StackDownGhcr }
    "^(stack-down-ghcr-wsl)$" { Task-StackDownGhcrWsl }
    "^(stack-status)$" { Task-StackStatus }
    "^(stack-logs)$" { Task-StackLogs }
    "^(stack-build)$" { Task-StackBuild }
    "^(stack-rebuild-backend-wsl)$" { Task-StackRebuildBackendWsl }
    "^(check-backend)$" { Task-CheckBackend }
    "^(check-web)$" { Task-CheckWeb }
    "^(check-bot)$" { Task-CheckBot }
    "^(frontend-install)$" { Task-FrontendInstall }
    "^(frontend-dev)$" { Task-FrontendDev }
    "^(frontend-lint)$" { Task-FrontendLint }
    "^(frontend-build)$" { Task-FrontendBuild }
    "^(help|-h|--help|\?)$" { Show-Help }
    default {
        Write-Host "Unknown target: $Task" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
