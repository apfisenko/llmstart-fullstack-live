import logging
import uuid

from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.infrastructure.llm_assistant import LlmInvocationError, StubLlmAssistant
from app.main import create_app
from tests.constants import (
    AUTH_HEADERS,
    AUTH_TOKEN,
    CHECKPOINT_1,
    COHORT_ID,
    MEMBERSHIP_ID,
    OTHER_MEMBERSHIP_ID,
    TEACHER_MEMBERSHIP_ID,
    USER_ID_A,
    USER_ID_TEACHER,
)


async def test_health_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_db_ok(client):
    response = await client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_post_dialogue_message_returns_assistant_reply(client):
    response = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "hello",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "dialogue_id" in data
    assert "user_message_id" in data
    assert data["assistant_message"]["content"] == "Echo:5"


async def test_post_dialogue_message_unknown_cohort_uses_ephemeral_llm(client):
    missing_cohort = uuid.uuid4()
    r = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "hello",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["assistant_message"]["content"] == "Echo:5"
    assert "dialogue_id" in data
    assert "user_message_id" in data


async def test_post_dialogue_message_unknown_cohort_continues_with_dialogue_id(client):
    missing_cohort = uuid.uuid4()
    mid = str(uuid.uuid4())
    first = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": mid,
            "channel": "web",
            "content": "hello",
        },
    )
    assert first.status_code == 200
    dialogue_id = first.json()["dialogue_id"]

    second = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": mid,
            "dialogue_id": dialogue_id,
            "channel": "web",
            "content": "ab",
        },
    )
    assert second.status_code == 200
    assert second.json()["dialogue_id"] == dialogue_id
    assert second.json()["assistant_message"]["content"] == "Echo:2"


async def test_post_dialogue_message_unknown_cohort_foreign_dialogue_id_forbidden(client):
    missing_cohort = uuid.uuid4()
    mid_a = str(uuid.uuid4())
    first = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": mid_a,
            "channel": "telegram",
            "content": "hello",
        },
    )
    dialogue_id = first.json()["dialogue_id"]
    second = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "dialogue_id": dialogue_id,
            "channel": "telegram",
            "content": "b",
        },
    )
    assert second.status_code == 403


async def test_post_dialogue_message_unknown_cohort_wrong_dialogue_id_forbidden(client):
    missing_cohort = uuid.uuid4()
    r = await client.post(
        f"/api/v1/cohorts/{missing_cohort}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "dialogue_id": str(uuid.uuid4()),
            "content": "x",
        },
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


async def test_post_dialogue_message_continues_same_dialogue_id(client):
    first = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "hello",
        },
    )
    assert first.status_code == 200
    dialogue_id = first.json()["dialogue_id"]

    second = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "dialogue_id": dialogue_id,
            "channel": "telegram",
            "content": "ab",
        },
    )
    assert second.status_code == 200
    assert second.json()["dialogue_id"] == dialogue_id
    assert second.json()["assistant_message"]["content"] == "Echo:2"


async def test_post_dialogue_message_validation_422(client):
    response = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
        },
    )
    assert response.status_code == 422


async def test_post_dialogue_message_unauthorized_wrong_bearer(client):
    response = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "x",
        },
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_post_dialogue_message_unauthorized_missing_bearer(
    monkeypatch, engine, session_factory, seed_data
):
    monkeypatch.setenv("BACKEND_API_CLIENT_TOKEN", AUTH_TOKEN)
    get_settings.cache_clear()
    app = create_app(
        engine=engine,
        session_factory=session_factory,
        llm=StubLlmAssistant(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
            json={
                "membership_id": str(MEMBERSHIP_ID),
                "channel": "telegram",
                "content": "x",
            },
        )
    get_settings.cache_clear()
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_v1_allowed_without_bearer_when_token_not_configured(client_no_auth):
    response = await client_no_auth.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "hi",
        },
    )
    assert response.status_code == 200


async def test_llm_failure_returns_503(monkeypatch, engine, session_factory, seed_data):
    monkeypatch.setenv("BACKEND_API_CLIENT_TOKEN", AUTH_TOKEN)
    get_settings.cache_clear()

    class FailingLlm:
        async def reply(self, turns: list[tuple[str, str]]) -> str:
            raise LlmInvocationError("simulated outage")

    app = create_app(
        engine=engine,
        session_factory=session_factory,
        llm=FailingLlm(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=AUTH_HEADERS,
    ) as ac:
        response = await ac.post(
            f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
            json={
                "membership_id": str(MEMBERSHIP_ID),
                "channel": "telegram",
                "content": "x",
            },
        )
    get_settings.cache_clear()
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "LLM_UNAVAILABLE"


async def test_dialogue_reset_returns_204(client):
    create = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "first",
        },
    )
    dialogue_id = create.json()["dialogue_id"]

    reset = await client.post(f"/api/v1/dialogues/{dialogue_id}/reset")
    assert reset.status_code == 204


async def test_dialogue_reset_clears_history_for_next_message(client):
    create = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "first",
        },
    )
    dialogue_id = create.json()["dialogue_id"]
    await client.post(f"/api/v1/dialogues/{dialogue_id}/reset")

    after = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "dialogue_id": dialogue_id,
            "channel": "telegram",
            "content": "after",
        },
    )
    assert after.status_code == 200
    assert after.json()["assistant_message"]["content"] == "Echo:5"


async def test_post_message_logs_do_not_contain_user_text(caplog, client):
    secret = "SECRET_USER_PLAINTEXT_XYZ_99"
    with caplog.at_level(logging.INFO):
        response = await client.post(
            f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
            json={
                "membership_id": str(MEMBERSHIP_ID),
                "channel": "telegram",
                "content": secret,
            },
        )
    assert response.status_code == 200
    combined = "\n".join(r.getMessage() for r in caplog.records)
    assert secret not in combined


async def test_post_guest_message_ok(client):
    response = await client.post(
        "/api/v1/assistant/guest/messages",
        json={"guest_session_key": "tg-guest-1", "content": "hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_message"]["content"] == "Echo:5"
    assert "id" in data["assistant_message"]


async def test_post_guest_reset_clears_session(client):
    key = "tg-guest-2"
    await client.post(
        "/api/v1/assistant/guest/messages",
        json={"guest_session_key": key, "content": "a"},
    )
    r2 = await client.post(
        "/api/v1/assistant/guest/messages",
        json={"guest_session_key": key, "content": "bbbb"},
    )
    assert r2.json()["assistant_message"]["content"] == "Echo:4"
    reset = await client.post(
        "/api/v1/assistant/guest/reset",
        json={"guest_session_key": key},
    )
    assert reset.status_code == 204
    r3 = await client.post(
        "/api/v1/assistant/guest/messages",
        json={"guest_session_key": key, "content": "cd"},
    )
    assert r3.json()["assistant_message"]["content"] == "Echo:2"


async def test_wrong_membership_for_dialogue_forbidden(client):
    create = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "telegram",
            "content": "a",
        },
    )
    dialogue_id = create.json()["dialogue_id"]

    response = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(OTHER_MEMBERSHIP_ID),
            "dialogue_id": dialogue_id,
            "channel": "telegram",
            "content": "b",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


async def test_list_progress_checkpoints_ok(client):
    r = await client.get(f"/api/v1/cohorts/{COHORT_ID}/progress-checkpoints")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["code"] == "w1"
    assert data["items"][0]["is_homework"] is False
    assert data["items"][1]["code"] == "hw_w2"
    assert data["items"][1]["is_homework"] is True


async def test_list_progress_checkpoints_not_found(client):
    r = await client.get(
        f"/api/v1/cohorts/{uuid.uuid4()}/progress-checkpoints",
    )
    assert r.status_code == 404


async def test_put_progress_record_ok(client):
    r = await client.put(
        f"/api/v1/cohorts/{COHORT_ID}/memberships/{MEMBERSHIP_ID}/progress-records/{CHECKPOINT_1}",
        json={
            "status": "completed",
            "comment": "done",
            "submission_links": ["https://example.com/a"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "completed"
    assert body["comment"] == "done"
    assert body["submission_links"] == ["https://example.com/a"]
    assert body["membership_id"] == str(MEMBERSHIP_ID)
    assert body["checkpoint_id"] == str(CHECKPOINT_1)


async def test_put_progress_teacher_forbidden(client):
    r = await client.put(
        f"/api/v1/cohorts/{COHORT_ID}/memberships/{TEACHER_MEMBERSHIP_ID}/"
        f"progress-records/{CHECKPOINT_1}",
        json={"status": "completed"},
    )
    assert r.status_code == 403


async def test_get_summary_as_teacher(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/summary",
        params={"viewer_membership_id": str(TEACHER_MEMBERSHIP_ID)},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["cohort_id"] == str(COHORT_ID)
    assert len(data["checkpoints"]) == 2
    assert len(data["participants"]) == 3
    student = next(p for p in data["participants"] if p["membership_id"] == str(MEMBERSHIP_ID))
    assert student["progress"][str(CHECKPOINT_1)] == "not_started"


async def test_get_summary_student_forbidden(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/summary",
        params={"viewer_membership_id": str(MEMBERSHIP_ID)},
    )
    assert r.status_code == 403


async def test_post_auth_dev_session_ok(client):
    r = await client.post(
        "/api/v1/auth/dev-session",
        json={"telegram_username": "@Student_A"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == str(USER_ID_A)
    assert any(m["membership_id"] == str(MEMBERSHIP_ID) for m in data["memberships"])
    for m in data["memberships"]:
        assert m["role"] in ("student", "teacher")
        assert "MembershipRole" not in m["role"]


async def test_post_auth_dev_session_teacher_role_value(client):
    r = await client.post(
        "/api/v1/auth/dev-session",
        json={"telegram_username": "fixture_teacher"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == str(USER_ID_TEACHER)
    assert len(data["memberships"]) == 1
    assert data["memberships"][0]["role"] == "teacher"


async def test_post_auth_dev_session_not_found(client):
    r = await client.post(
        "/api/v1/auth/dev-session",
        json={"telegram_username": "nope_missing_user"},
    )
    assert r.status_code == 404


async def test_get_teacher_dashboard_ok(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/teacher-dashboard",
        params={"viewer_membership_id": str(TEACHER_MEMBERSHIP_ID)},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["cohort_id"] == str(COHORT_ID)
    assert "kpis" in data
    assert "activity_by_day" in data
    assert "recent_turns" in data
    assert "matrix" in data


async def test_get_teacher_dashboard_student_forbidden(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/teacher-dashboard",
        params={"viewer_membership_id": str(MEMBERSHIP_ID)},
    )
    assert r.status_code == 403


async def test_get_leaderboard_ok(client):
    r = await client.get(f"/api/v1/cohorts/{COHORT_ID}/leaderboard")
    assert r.status_code == 200
    data = r.json()
    assert data["cohort_id"] == str(COHORT_ID)
    assert len(data["checkpoints"]) == 2
    assert len(data["entries"]) >= 2


async def test_get_progress_overview_ok(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/memberships/{MEMBERSHIP_ID}/progress-overview",
    )
    assert r.status_code == 200
    data = r.json()
    assert data["membership_id"] == str(MEMBERSHIP_ID)
    assert len(data["checkpoints"]) == 2
    assert len(data["records"]) == 2


async def test_get_progress_overview_teacher_forbidden(client):
    r = await client.get(
        f"/api/v1/cohorts/{COHORT_ID}/memberships/{TEACHER_MEMBERSHIP_ID}/progress-overview",
    )
    assert r.status_code == 403


async def test_list_dialogue_turns_ok(client):
    create = await client.post(
        f"/api/v1/cohorts/{COHORT_ID}/dialogues/messages",
        json={
            "membership_id": str(MEMBERSHIP_ID),
            "channel": "web",
            "content": "hello",
        },
    )
    dialogue_id = create.json()["dialogue_id"]
    r = await client.get(f"/api/v1/dialogues/{dialogue_id}/turns", params={"limit": 10})
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["question_text"] == "hello"
