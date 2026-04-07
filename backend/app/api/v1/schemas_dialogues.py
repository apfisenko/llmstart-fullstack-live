from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ClientChannel(str, Enum):
    telegram = "telegram"
    web = "web"


class PostDialogueMessageRequest(BaseModel):
    membership_id: UUID
    dialogue_id: Optional[UUID] = None
    channel: ClientChannel
    content: str = Field(min_length=1)


class AssistantMessageBlock(BaseModel):
    id: UUID
    content: str
    created_at: str


class PostDialogueMessageResponse(BaseModel):
    dialogue_id: UUID
    user_message_id: UUID
    assistant_message: AssistantMessageBlock
