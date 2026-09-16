"""Document ORM model. Full-text search over title + description + category."""
from sqlalchemy import ARRAY, BigInteger, Computed, Date, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base


class DocumentModel(AuditMixin, Base):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    file_name: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    file_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    expiry_date: Mapped[Date | None] = mapped_column(Date, nullable=True)

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', title || ' ' || coalesce(description, '') || ' ' || coalesce(category, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_documents_search_vector", "search_vector", postgresql_using="gin"),
    )
