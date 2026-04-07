from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.schemas_dialogues import AssistantMessageBlock


class PostGuestMessageRequest(BaseModel):
    guest_session_key: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1)


class PostGuestMessageResponse(BaseModel):
    assistant_message: AssistantMessageBlock


class PostGuestResetRequest(BaseModel):
    guest_session_key: str = Field(min_length=1, max_length=256)
