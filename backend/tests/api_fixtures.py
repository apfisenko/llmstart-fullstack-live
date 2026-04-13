"""Общие async-фикстуры API-тестов (подключаются из tests/conftest.py)."""

from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.domain import models  # noqa: F401
from app.domain.base import Base
from app.domain.models import (
    Cohort,
    CohortMembership,
    MembershipRole,
    MembershipStatus,
    ProgressCheckpoint,
    User,
)
from app.infrastructure.llm_assistant import StubLlmAssistant
from app.main import create_app
from tests.constants import (
    AUTH_HEADERS,
    AUTH_TOKEN,
    CHECKPOINT_1,
    CHECKPOINT_2,
    COHORT_ID,
    MEMBERSHIP_ID,
    OTHER_MEMBERSHIP_ID,
    TEACHER_MEMBERSHIP_ID,
    USER_ID_A,
    USER_ID_B,
    USER_ID_C,
    USER_ID_TEACHER,
)


@pytest_asyncio.fixture
async def engine():
    get_settings.cache_clear()
    settings = get_settings()
    url = settings.database_url
    eng = create_async_engine(url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def seed_data(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        session.add(User(id=USER_ID_A, name="Student A"))
        session.add(User(id=USER_ID_B, name="Student B"))
        session.add(User(id=USER_ID_C, name="Extra"))
        session.add(User(id=USER_ID_TEACHER, name="Teacher"))
        session.add(Cohort(id=COHORT_ID, title="Test cohort", code="test"))
        await session.flush()
        session.add(
            CohortMembership(
                id=MEMBERSHIP_ID,
                user_id=USER_ID_A,
                cohort_id=COHORT_ID,
                role=MembershipRole.student,
                status=MembershipStatus.active,
            )
        )
        session.add(
            CohortMembership(
                id=OTHER_MEMBERSHIP_ID,
                user_id=USER_ID_B,
                cohort_id=COHORT_ID,
                role=MembershipRole.student,
                status=MembershipStatus.active,
            )
        )
        session.add(
            CohortMembership(
                id=TEACHER_MEMBERSHIP_ID,
                user_id=USER_ID_TEACHER,
                cohort_id=COHORT_ID,
                role=MembershipRole.teacher,
                status=MembershipStatus.active,
            )
        )
        session.add(
            ProgressCheckpoint(
                id=CHECKPOINT_1,
                cohort_id=COHORT_ID,
                code="w1",
                title="Week 1",
                sort_order=1,
                required=True,
            )
        )
        session.add(
            ProgressCheckpoint(
                id=CHECKPOINT_2,
                cohort_id=COHORT_ID,
                code="w2",
                title="Week 2",
                sort_order=2,
                required=False,
            )
        )
        await session.commit()
    yield


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def client(monkeypatch, engine, session_factory, seed_data):
    monkeypatch.setenv("BACKEND_API_CLIENT_TOKEN", AUTH_TOKEN)
    get_settings.cache_clear()
    app = create_app(
        engine=engine,
        session_factory=session_factory,
        llm=StubLlmAssistant(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=AUTH_HEADERS,
    ) as ac:
        yield ac
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client_no_auth(monkeypatch, engine, session_factory, seed_data):
    monkeypatch.delenv("BACKEND_API_CLIENT_TOKEN", raising=False)
    get_settings.cache_clear()
    app = create_app(
        engine=engine,
        session_factory=session_factory,
        llm=StubLlmAssistant(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    get_settings.cache_clear()
