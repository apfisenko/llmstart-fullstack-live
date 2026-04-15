from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.api.v1.schemas_progress import ProgressCheckpointItem, ProgressStatusEnum


class PostAuthDevSessionRequest(BaseModel):
    telegram_username: str = Field(min_length=1, max_length=255)


class DevSessionMembershipItem(BaseModel):
    membership_id: UUID
    cohort_id: UUID
    cohort_title: Optional[str] = None
    role: str


class PostAuthDevSessionResponse(BaseModel):
    user_id: UUID
    display_name: Optional[str] = None
    memberships: list[DevSessionMembershipItem]
    web_dialogue_id: Optional[UUID] = None


class KpiWeekPair(BaseModel):
    current_week: int = Field(ge=0)
    previous_week: int = Field(ge=0)


class AvgProgressWeekPair(BaseModel):
    current_week: float = Field(ge=0, le=100)
    previous_week: float = Field(ge=0, le=100)


class TeacherDashboardKpis(BaseModel):
    active_students: KpiWeekPair
    homework_completed_events: KpiWeekPair
    avg_progress_percent: AvgProgressWeekPair
    dialogue_questions: KpiWeekPair


class ActivityByDayItem(BaseModel):
    day: str
    question_count: int = Field(ge=0)


class DashboardDialogueTurnItem(BaseModel):
    membership_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    student_display_name: Optional[str] = None
    question_text: str
    answer_text: str
    asked_at: str


class DashboardRecentSubmissionItem(BaseModel):
    membership_id: UUID
    student_display_name: Optional[str] = None
    checkpoint_id: UUID
    checkpoint_title: str
    status: ProgressStatusEnum
    comment: Optional[str] = None
    submission_links: Optional[list[str]] = None
    updated_at: str


class DashboardMatrixCell(BaseModel):
    checkpoint_id: UUID
    status: ProgressStatusEnum
    updated_at: Optional[str] = None


class DashboardMatrixRow(BaseModel):
    membership_id: UUID
    display_name: Optional[str] = None
    score_completed: int = Field(ge=0)
    score_total: int = Field(ge=0)
    cells: list[DashboardMatrixCell]


class TeacherDashboardRecentTurns(BaseModel):
    items: list[DashboardDialogueTurnItem]
    next_cursor: Optional[str] = None


class TeacherDashboardResponse(BaseModel):
    cohort_id: UUID
    cohort_title: Optional[str] = None
    kpis: TeacherDashboardKpis
    activity_by_day: list[ActivityByDayItem]
    recent_turns: TeacherDashboardRecentTurns
    recent_submissions: list[DashboardRecentSubmissionItem]
    matrix: list[DashboardMatrixRow]


class LeaderboardCheckpointStatus(BaseModel):
    checkpoint_id: UUID
    status: ProgressStatusEnum


class LeaderboardEntry(BaseModel):
    rank: int = Field(ge=1)
    membership_id: UUID
    user_id: UUID
    display_name: Optional[str] = None
    progress_percent: float = Field(ge=0, le=100)
    completed_checkpoints: int = Field(ge=0)
    total_checkpoints: int = Field(ge=0)
    homework_completed: int = Field(ge=0)
    lesson_completed: int = Field(ge=0)
    scatter_x: Optional[float] = None
    scatter_y: Optional[float] = None
    per_checkpoint: list[LeaderboardCheckpointStatus]


class LeaderboardResponse(BaseModel):
    cohort_id: UUID
    checkpoints: list[ProgressCheckpointItem]
    entries: list[LeaderboardEntry]


class StudentProgressRecordItem(BaseModel):
    checkpoint_id: UUID
    status: ProgressStatusEnum
    updated_at: Optional[str] = None
    comment: Optional[str] = None
    submission_links: Optional[list[str]] = None


class StudentProgressOverviewResponse(BaseModel):
    cohort_id: UUID
    membership_id: UUID
    display_name: Optional[str] = None
    checkpoints: list[ProgressCheckpointItem]
    records: list[StudentProgressRecordItem]


class DialogueTurnListItem(BaseModel):
    user_message_id: UUID
    assistant_message_id: UUID
    question_text: str
    answer_text: str
    asked_at: str
    answered_at: str


class DialogueTurnsListResponse(BaseModel):
    items: list[DialogueTurnListItem]
    next_before_asked_at: Optional[str] = None
