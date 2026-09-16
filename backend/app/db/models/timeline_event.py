"""
TimelineEvent ORM model. Deliberately does NOT use AuditMixin: this is an
append-only event log (no update, no soft delete — an event happened or
it didn't). Only `id` and `created_at` are needed, plus `occurred_at`
which is currently always equal to `created_at` but kept as a separate
column so a future backfill/import feature could set a historical date
without conflating it with row-insertion time.
"""
import uuid

from sqlalchemy import Computed, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.timeline.entity import TimelineEventType


class TimelineEventModel(Base):
    __tablename__ = "timeline_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_type: Mapped[TimelineEventType] = mapped_column(
        Enum(TimelineEventType, name="timeline_event_type"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    occurred_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', title)", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_timeline_events_occurred_at", "occurred_at"),
        Index("ix_timeline_events_search_vector", "search_vector", postgresql_using="gin"),
    )
