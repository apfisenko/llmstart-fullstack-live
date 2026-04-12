from __future__ import annotations

import importlib
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.errors import ApiError
from app.api.v1.router import router as api_v1_router
from app.config import Settings, get_settings
from app.domain.base import Base
from app.infrastructure.database import create_engine_and_session_factory
from app.infrastructure.llm_assistant import (
    LlmAssistant,
    LlmInvocationError,
    OpenRouterLlmAssistant,
    StubLlmAssistant,
)
from app.services.guest_dialogue_service import GuestDialogueService

logger = logging.getLogger(__name__)


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

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        level_name = os.environ.get("LOG_LEVEL", "INFO")
        level = getattr(logging, level_name.upper(), logging.INFO)
        logging.basicConfig(level=level, format="%(levelname)s %(name)s %(message)s")

        if "sqlite" in resolved_settings.database_url:
            importlib.import_module("app.domain.models")

            async with eng.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

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
    if llm_override is not None:
        application.state.llm = llm_override
        # ASGI-транспорт в тестах может отработать запрос до lifespan; guest нужен сразу.
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

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    @application.get("/health/db")
    async def health_db(request: Request):
        engine = request.app.state.engine
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:
            logger.exception("Database health check failed")
            return JSONResponse(
                status_code=503,
                content={"status": "error", "database": "unavailable"},
            )
        return {"status": "ok", "database": "ok"}

    return application


app = create_app()
