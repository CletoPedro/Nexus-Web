"""
Inventory ORM model. `document_id` is a nullable FK to `documents` (e.g.
"Laptop -> Warranty PDF"). Soft deletes never physically remove rows, so
the FK stays valid even after a referenced document is soft-deleted.
"""
from sqlalchemy import (
    ARRAY,
    Computed,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base


class InventoryItemModel(AuditMixin, Base):
    __tablename__ = "inventory_items"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    purchase_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[Numeric | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    serial_number: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', name || ' ' || coalesce(description, '') || ' ' || coalesce(category, '') || ' ' || coalesce(location, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_inventory_items_search_vector", "search_vector", postgresql_using="gin"
        ),
    )
