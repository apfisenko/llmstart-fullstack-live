param([string]$cmd = "run")

switch ($cmd) {
    "install" {
        python -m pip install --proxy http://127.0.0.1:1301 --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
    }
    "run" {
        python -m bot.main
    }
    "lint" {
        python -m ruff check .
        python -m ruff format --check .
    }
    "format" {
        python -m ruff format .
        python -m ruff check --fix .
    }
    default {
        Write-Host "Команды: install | run | lint | format"
        Write-Host "Пример: .\run.ps1 run"
    }
}
