"""
Memory ORM model. Includes a Postgres tsvector column + GIN index for
full-text search, per Phase W1 architecture section 5 — Universal Search
(and this module's own search) works without any AI involvement.
"""
from sqlalchemy import ARRAY, Computed, DateTime, Index, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base


class MemoryModel(AuditMixin, Base):
    __tablename__ = "memories"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    expires_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Generated column kept in sync by Postgres itself, indexed for search.
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_memories_search_vector", "search_vector", postgresql_using="gin"),
    )
