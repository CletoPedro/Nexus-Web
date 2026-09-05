"""Inventory domain entity. Framework-independent, per W1 architecture."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


@dataclass
class InventoryItem:
    name: str
    description: str = ""
    category: str = ""
    location: str = ""
    quantity: int = 1
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    serial_number: str = ""
    document_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None
