"""Общие константы для API-тестов (conftest + модули тестов)."""

import uuid

COHORT_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
MEMBERSHIP_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
OTHER_MEMBERSHIP_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")
TEACHER_MEMBERSHIP_ID = uuid.UUID("44444444-4444-4444-8444-444444444444")

USER_ID_A = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
USER_ID_B = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
USER_ID_C = uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
USER_ID_TEACHER = uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")

CHECKPOINT_1 = uuid.UUID("aaaaaaaa-bbbb-4ccc-8ddd-111111111111")
CHECKPOINT_2 = uuid.UUID("aaaaaaaa-bbbb-4ccc-8ddd-222222222222")

AUTH_TOKEN = "test-bearer-token"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}
