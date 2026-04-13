#requires -Version 5.1
<#
.SYNOPSIS
  Makefile-like tasks for Windows PowerShell (dev, DB, tests).

.DESCRIPTION
  Run from repo root: .\tasks.ps1 install | db-up | db-migrate | test-backend ...

  Если в PowerShell нет `docker` в PATH, скрипт сам использует `wsl -e docker compose`
  (Docker только внутри WSL). Иначе можно задать вручную:
    $env:DOCKER_COMPOSE = "wsl -d Ubuntu -e docker compose"; .\tasks.ps1 db-up

  Env vars (same as Makefile): POSTGRES_*, DATABASE_URL, TEST_DATABASE_URL, DOCKER_COMPOSE.
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

function Get-PostgresDatabaseUrl {
    return "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_DB)"
}

function Wait-PostgresPort {
    param(
        [string] $ComputerName = "127.0.0.1",
        [int] $Port = 5432,
        [int] $TimeoutSec = 90
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $tcp = $null
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect($ComputerName, $Port)
            if ($tcp.Connected) { return }
        }
        catch {
            # порт ещё не слушает — повторяем
        }
        finally {
            if ($null -ne $tcp) { $tcp.Close() }
        }
        Start-Sleep -Milliseconds 300
    }
    throw "PostgreSQL недоступен на ${ComputerName}:${Port} за $TimeoutSec с (после docker compose up)."
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

function Task-Run {
    uv run python -m bot.main
}

function Task-Lint {
    uv run ruff check bot
    uv run ruff format --check bot
    Invoke-Backend @("uv", "run", "ruff", "check", "app", "tests")
    Invoke-Backend @("uv", "run", "ruff", "format", "--check", "app", "tests")
}

function Task-Format {
    uv run ruff format bot
    uv run ruff check --fix bot
    Invoke-Backend @("uv", "run", "ruff", "format", "app", "tests")
    Invoke-Backend @("uv", "run", "ruff", "check", "--fix", "app", "tests")
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
    Invoke-DockerCompose @("up", "-d", "--wait")
    Wait-PostgresPort
    Task-DbMigrateAll
}

function Task-DbDown {
    Invoke-DockerCompose @("down")
}

function Task-DbReset {
    Invoke-DockerCompose @("down", "-v")
    Invoke-DockerCompose @("up", "-d", "--wait")
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

function Show-Help {
    Write-Host @"
Usage: .\tasks.ps1 <target>

  install                 uv sync (repo root + backend)
  run                     bot: uv run python -m bot.main
  lint, backend-lint      ruff (bot + backend)
  format                  ruff format + fix
  test, test-backend, backend-test, test-all
                          pytest tests/pg (PostgreSQL)
  backend-dev             uvicorn --reload
  backend-typecheck       note about mypy
  db-up, db-down          docker compose; после db-up — миграции на llmstart и llmstart_test
  db-reset                down -v, up --wait, миграции на обе БД
  db-migrate, migrate-backend
                          только llmstart: uv sync --extra dev; alembic upgrade head
  db-migrate-test-db      только POSTGRES_TEST_DB (Alembic)
  db-migrate-all          db-migrate + db-test-create + db-migrate-test-db
  db-test-create          CREATE llmstart_test if missing (pytest DB)
  db-migrate-test, migrate-backend-test
                          db-migrate-all + pytest tests/pg
  db-shell                psql in postgres container

Env: DOCKER_COMPOSE, POSTGRES_*, POSTGRES_TEST_DB, DATABASE_URL, TEST_DATABASE_URL (see Makefile).

Docker только в WSL: если `docker` не в PATH Windows, скрипт вызывает `wsl -e docker compose`.
Свой дистрибутив: `$env:DOCKER_COMPOSE = 'wsl -d Ubuntu -e docker compose'`
"@
}

switch -Regex ($Task.ToLowerInvariant()) {
    "^(install)$" { Task-Install }
    "^(run)$" { Task-Run }
    "^(lint|backend-lint)$" { Task-Lint }
    "^(format)$" { Task-Format }
    "^(test|test-backend|backend-test|test-all)$" { Task-TestBackend }
    "^(backend-dev)$" { Task-BackendDev }
    "^(backend-typecheck)$" { Task-BackendTypecheck }
    "^(db-up)$" { Task-DbUp }
    "^(db-down)$" { Task-DbDown }
    "^(db-migrate|migrate-backend)$" { Task-DbMigrate }
    "^(db-migrate-test-db)$" { Task-DbMigrateTestDb }
    "^(db-migrate-all)$" { Task-DbMigrateAll }
    "^(db-reset)$" { Task-DbReset }
    "^(db-test-create)$" { Task-DbTestCreate }
    "^(db-migrate-test|migrate-backend-test)$" { Task-DbMigrateTest }
    "^(db-shell)$" { Task-DbShell }
    "^(help|-h|--help|\?)$" { Show-Help }
    default {
        Write-Host "Unknown target: $Task" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
