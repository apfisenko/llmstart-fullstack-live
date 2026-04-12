#requires -Version 5.1
<#
.SYNOPSIS
  Makefile-like tasks for Windows PowerShell (dev, DB, tests).

.DESCRIPTION
  Run from repo root: .\tasks.ps1 install | db-up | db-migrate | test-backend ...

  If docker is only in WSL:
    $env:DOCKER_COMPOSE = "wsl -e docker compose"; .\tasks.ps1 db-up

  Env vars (same as Makefile): POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DATABASE_URL, DOCKER_COMPOSE.
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
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_DB)"
}
if (-not $env:TEST_DATABASE_URL) {
    $env:TEST_DATABASE_URL = "postgresql+asyncpg://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@127.0.0.1:5432/$($env:POSTGRES_TEST_DB)"
}

function Invoke-DockerCompose {
    param([string[]] $ArgumentList)
    $prefix = if ($env:DOCKER_COMPOSE) { $env:DOCKER_COMPOSE.Trim() } else { "docker compose" }
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

function Task-TestBackendSqlite {
    Invoke-Backend @("uv", "sync", "--extra", "dev")
    Invoke-Backend @("uv", "run", "pytest", "tests/sqlite")
}

function Task-TestAll {
    Task-TestBackend
    Task-TestBackendSqlite
}

function Task-DbTestCreate {
    $db = $env:POSTGRES_TEST_DB
    $prefix = if ($env:DOCKER_COMPOSE) { $env:DOCKER_COMPOSE.Trim() } else { "docker compose" }
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

function Task-DbUp {
    Invoke-DockerCompose @("up", "-d", "--wait")
}

function Task-DbDown {
    Invoke-DockerCompose @("down")
}

function Task-DbMigrate {
    Invoke-Backend @("uv", "sync", "--extra", "dev")
    Invoke-Backend @("uv", "run", "alembic", "upgrade", "head")
}

function Task-DbReset {
    Invoke-DockerCompose @("down", "-v")
    Invoke-DockerCompose @("up", "-d", "--wait")
    Task-DbMigrate
}

function Task-DbMigrateTest {
    Task-DbMigrate
    Task-DbTestCreate
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
  test, test-backend, backend-test
                          pytest tests/pg (PostgreSQL)
  test-backend-sqlite, backend-test-sqlite
                          pytest tests/sqlite (SQLite in-memory)
  test-all                test-backend then test-backend-sqlite
  backend-dev             uvicorn --reload
  backend-typecheck       note about mypy
  db-up, db-down          docker compose
  db-reset                down -v, up --wait, migrate
  db-migrate, migrate-backend
  db-test-create          CREATE llmstart_test if missing (pytest DB)
  db-migrate-test, migrate-backend-test
  db-shell                psql in postgres container

Env: DOCKER_COMPOSE, POSTGRES_*, POSTGRES_TEST_DB, DATABASE_URL, TEST_DATABASE_URL (see Makefile).

Docker via WSL only:
  `$env:DOCKER_COMPOSE = 'wsl -e docker compose'; .\tasks.ps1 db-up
"@
}

switch -Regex ($Task.ToLowerInvariant()) {
    "^(install)$" { Task-Install }
    "^(run)$" { Task-Run }
    "^(lint|backend-lint)$" { Task-Lint }
    "^(format)$" { Task-Format }
    "^(test|test-backend|backend-test)$" { Task-TestBackend }
    "^(test-backend-sqlite|backend-test-sqlite)$" { Task-TestBackendSqlite }
    "^(test-all)$" { Task-TestAll }
    "^(backend-dev)$" { Task-BackendDev }
    "^(backend-typecheck)$" { Task-BackendTypecheck }
    "^(db-up)$" { Task-DbUp }
    "^(db-down)$" { Task-DbDown }
    "^(db-migrate|migrate-backend)$" { Task-DbMigrate }
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
