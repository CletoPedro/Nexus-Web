"""Pydantic schemas for the Inventory API."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=10_000)
    category: str = Field(default="", max_length=100)
    location: str = Field(default="", max_length=200)
    quantity: int = Field(default=1, ge=0)
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    serial_number: str = Field(default="", max_length=200)
    document_id: uuid.UUID | None = None


class InventoryItemUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10_000)
    category: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    quantity: int | None = Field(default=None, ge=0)
    document_id: uuid.UUID | None = None
    document_id_provided: bool = False


class InventoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str
    category: str
    location: str
    quantity: int
    purchase_date: date | None
    purchase_price: Decimal | None
    serial_number: str
    document_id: uuid.UUID | None
    created_at: datetime | None
    updated_at: datetime | None
