# syntax=docker/dockerfile:1
# Сборка из корня: docker build -f devops/bot/Dockerfile .
FROM python:3.12.8-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_HTTP_TIMEOUT=300 \
    UV_HTTP_RETRIES=5

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY bot ./bot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

RUN useradd --create-home --uid 10002 botuser \
    && chown -R botuser:botuser /app

USER botuser
ENV PATH="/app/.venv/bin:$PATH"

# HTTP healthcheck не подходит: long polling к Telegram, а проверка backend даёт ложный «unhealthy»
# при кратковременных сбоях API и не отражает состояние процесса бота.

CMD ["python", "-m", "bot.main"]
