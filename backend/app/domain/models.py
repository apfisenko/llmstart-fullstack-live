from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import Base


class MembershipRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"


class MembershipStatus(str, enum.Enum):
    active = "active"
    withdrawn = "withdrawn"


class DialogueChannel(str, enum.Enum):
    telegram = "telegram"
    web = "web"


class DialogueState(str, enum.Enum):
    active = "active"
    archived = "archived"


class ProgressStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memberships: Mapped[list[CohortMembership]] = relationship(back_populates="user")


class Cohort(Base):
    __tablename__ = "cohorts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memberships: Mapped[list[CohortMembership]] = relationship(back_populates="cohort")
    checkpoints: Mapped[list[ProgressCheckpoint]] = relationship(back_populates="cohort")


class CohortMembership(Base):
    __tablename__ = "cohort_memberships"
    __table_args__ = (UniqueConstraint("user_id", "cohort_id", name="uq_user_cohort"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    cohort_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MembershipRole] = mapped_column(
        SAEnum(MembershipRole, name="membership_role", native_enum=False),
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        SAEnum(MembershipStatus, name="membership_status", native_enum=False),
        nullable=False,
        default=MembershipStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="memberships")
    cohort: Mapped[Cohort] = relationship(back_populates="memberships")
    dialogues: Mapped[list[Dialogue]] = relationship(back_populates="membership")
    progress_records: Mapped[list[ProgressRecord]] = relationship(back_populates="membership")


class Dialogue(Base):
    __tablename__ = "dialogues"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cohort_memberships.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel: Mapped[DialogueChannel] = mapped_column(
        SAEnum(DialogueChannel, name="dialogue_channel", native_enum=False),
        nullable=False,
    )
    state: Mapped[DialogueState] = mapped_column(
        SAEnum(DialogueState, name="dialogue_state", native_enum=False),
        nullable=False,
        default=DialogueState.active,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    membership: Mapped[CohortMembership] = relationship(back_populates="dialogues")
    turns: Mapped[list[DialogueTurn]] = relationship(
        back_populates="dialogue",
        order_by="DialogueTurn.asked_at",
    )


class DialogueTurn(Base):
    __tablename__ = "dialogue_turns"
    __table_args__ = (
        UniqueConstraint(
            "assistant_message_id",
            name="uq_dialogue_turns_assistant_message_id",
        ),
        CheckConstraint(
            "answered_at >= asked_at",
            name="ck_dialogue_turns_answer_after_question",
        ),
        Index("ix_dialogue_turns_dialogue_asked", "dialogue_id", "asked_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assistant_message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )
    dialogue_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("dialogues.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    asked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dialogue: Mapped[Dialogue] = relationship(back_populates="turns")


class ProgressCheckpoint(Base):
    __tablename__ = "progress_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_homework: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    cohort: Mapped[Cohort] = relationship(back_populates="checkpoints")
    records: Mapped[list[ProgressRecord]] = relationship(back_populates="checkpoint")


class ProgressRecord(Base):
    __tablename__ = "progress_records"
    __table_args__ = (
        UniqueConstraint(
            "membership_id",
            "checkpoint_id",
            name="uq_membership_checkpoint",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cohort_memberships.id", ondelete="CASCADE"),
        nullable=False,
    )
    checkpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("progress_checkpoints.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(ProgressStatus, name="progress_status", native_enum=False),
        nullable=False,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submission_links: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    membership: Mapped[CohortMembership] = relationship(
        back_populates="progress_records",
    )
    checkpoint: Mapped[ProgressCheckpoint] = relationship(back_populates="records")
