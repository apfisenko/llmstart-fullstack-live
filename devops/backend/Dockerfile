# syntax=docker/dockerfile:1
# Сборка из корня: docker build -f devops/backend/Dockerfile .
FROM python:3.12.8-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_HTTP_TIMEOUT=300 \
    UV_HTTP_RETRIES=5

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
COPY backend/alembic.ini ./
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY bot/prompts ./bot/prompts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra dev

COPY devops/backend/docker-entrypoint.sh /docker-entrypoint.sh
# На Windows в репозитории часто CRLF — в Linux shebang ломается («no such file» для /bin/sh\r).
RUN sed -i 's/\r$//' /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /docker-entrypoint.sh

USER appuser
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Compose переопределяет healthcheck; для docker run без compose — те же сроки.
HEALTHCHECK --interval=15s --timeout=10s --start-period=300s --retries=5 CMD ["/app/.venv/bin/python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health', timeout=5).read()"]

ENTRYPOINT ["/docker-entrypoint.sh"]
