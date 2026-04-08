from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProgressStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class ParticipantRole(str, Enum):
    student = "student"
    teacher = "teacher"


class ProgressCheckpointItem(BaseModel):
    id: UUID
    code: str
    title: str
    sort_order: int
    required: bool


class ProgressCheckpointListResponse(BaseModel):
    items: list[ProgressCheckpointItem]


class PutProgressRecordRequest(BaseModel):
    status: ProgressStatusEnum
    comment: Optional[str] = Field(default=None, max_length=2000)


class ProgressRecordResponse(BaseModel):
    id: UUID
    cohort_id: UUID
    membership_id: UUID
    checkpoint_id: UUID
    status: ProgressStatusEnum
    comment: Optional[str] = None
    updated_at: str


class CohortSummaryParticipant(BaseModel):
    membership_id: UUID
    user_id: UUID
    role: ParticipantRole
    name: Optional[str] = None
    progress: dict[str, ProgressStatusEnum]


class CohortSummaryResponse(BaseModel):
    cohort_id: UUID
    cohort_title: Optional[str] = None
    checkpoints: list[ProgressCheckpointItem]
    participants: list[CohortSummaryParticipant]
