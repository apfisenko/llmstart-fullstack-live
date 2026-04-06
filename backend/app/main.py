import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    level_name = os.environ.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s %(name)s %(message)s")
    yield


def create_app() -> FastAPI:
    application = FastAPI(title="LLMStart Backend", lifespan=lifespan)
    application.include_router(api_v1_router)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
