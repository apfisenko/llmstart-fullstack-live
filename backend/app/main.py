from __future__ import annotations

import errno
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.errors import ApiError
from app.api.v1.router import router as api_v1_router
from app.config import Settings, get_settings
from app.infrastructure.database import create_engine_and_session_factory
from app.infrastructure.llm_assistant import (
    LlmAssistant,
    LlmInvocationError,
    OpenRouterLlmAssistant,
    StubLlmAssistant,
)
from app.services.guest_dialogue_service import GuestDialogueService

logger = logging.getLogger(__name__)


def _database_unavailable_response() -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "DATABASE_UNAVAILABLE",
                "message": (
                    "Cannot connect to PostgreSQL. Start the database (e.g. "
                    "`make db-up` / `tasks.ps1 db-up`) and check DATABASE_URL in backend/.env."
                ),
                "details": None,
            }
        },
    )


def create_app(
    *,
    settings: Optional[Settings] = None,
    engine: Optional[AsyncEngine] = None,
    session_factory: Optional[async_sessionmaker[AsyncSession]] = None,
    llm: Optional[LlmAssistant] = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    if engine is not None and session_factory is not None:
        eng, sess_factory = engine, session_factory
        dispose_engine_on_shutdown = False
    elif engine is None and session_factory is None:
        eng, sess_factory = create_engine_and_session_factory(resolved_settings)
        dispose_engine_on_shutdown = True
    else:
        raise ValueError("engine and session_factory must both be set or both omitted")

    llm_override = llm
    _db_url_parsed = make_url(resolved_settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        level_name = os.environ.get("LOG_LEVEL", "INFO")
        level = getattr(logging, level_name.upper(), logging.INFO)
        logging.basicConfig(level=level, format="%(levelname)s %(name)s %(message)s")
        logger.info(
            "backend_db_target host=%s port=%s driver=%s",
            _db_url_parsed.host,
            _db_url_parsed.port,
            _db_url_parsed.drivername,
        )

        if llm_override is None:
            if resolved_settings.openrouter_api_key:
                timeout = httpx.Timeout(resolved_settings.openrouter_timeout)
                proxies = (
                    resolved_settings.proxy_url if resolved_settings.proxy_url.strip() else None
                )
                client = httpx.AsyncClient(timeout=timeout, proxy=proxies)
                app.state.http_client = client
                app.state.llm = OpenRouterLlmAssistant(resolved_settings, client)
            else:
                app.state.llm = StubLlmAssistant()

        if getattr(app.state, "guest_dialogue", None) is None:
            app.state.guest_dialogue = GuestDialogueService(app.state.llm)

        yield

        http_client = getattr(app.state, "http_client", None)
        if http_client is not None:
            await http_client.aclose()
        if dispose_engine_on_shutdown:
            await eng.dispose()

    application = FastAPI(title="LLMStart Backend", lifespan=lifespan)
    application.state.engine = eng
    application.state.session_factory = sess_factory
    application.state.database_connect_target = (
        f"{_db_url_parsed.host}:{_db_url_parsed.port}"
        if _db_url_parsed.host
        else ""
    )
    if llm_override is not None:
        application.state.llm = llm_override
        application.state.guest_dialogue = GuestDialogueService(llm_override)
    application.include_router(api_v1_router)

    @application.exception_handler(ApiError)
    async def api_error_handler(_request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": None,
                }
            },
        )

    @application.exception_handler(LlmInvocationError)
    async def llm_error_handler(_request, exc: LlmInvocationError):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": None,
                }
            },
        )

    @application.exception_handler(OperationalError)
    async def sqlalchemy_operational_error_handler(_request, exc: OperationalError):
        logger.exception("database_operational_error")
        return _database_unavailable_response()

    @application.exception_handler(ConnectionRefusedError)
    async def connection_refused_handler(_request, exc: ConnectionRefusedError):
        logger.exception("database_connection_refused")
        return _database_unavailable_response()

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    @application.get("/health/db")
    async def health_db(request: Request):
        engine = request.app.state.engine
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as exc:
            logger.exception("Database health check failed")
            detail: dict = {"exception": type(exc).__name__}
            if isinstance(exc, OSError):
                detail["errno"] = getattr(exc, "errno", None)
            msg = str(exc).split("\n", 1)[0].strip()
            if msg and len(msg) < 240:
                detail["message"] = msg
            target = getattr(request.app.state, "database_connect_target", None)
            if target:
                detail["connect_target"] = target

            conn_refused = isinstance(exc, ConnectionRefusedError) or (
                isinstance(exc, OSError) and getattr(exc, "errno", None) == errno.ECONNREFUSED
            )
            if conn_refused:
                hint = (
                    "Отказ TCP к connect_target (detail): backend не туда, что db-status, "
                    "или другой DATABASE_URL в IDE. backend/.env теперь по пути к файлу. "
                    "Перезапустите backend. Затем: .\\tasks.ps1 db-up, .\\tasks.ps1 db-status."
                )
            else:
                hint = (
                    "Проверьте DATABASE_URL в backend/.env (логин/пароль/имя БД). "
                    "С Docker на Windows лучше 127.0.0.1, не localhost (::1). "
                    "После правки .env перезапустите uvicorn."
                )

            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "database": "unavailable",
                    "detail": detail,
                    "hint": hint,
                },
            )
        return {"status": "ok", "database": "ok"}

    return application


app = create_app()
