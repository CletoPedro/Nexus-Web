"""Pydantic schemas for the Memory API — the HTTP-facing contract."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class MemoryUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
    tags: list[str] | None = None
    metadata: dict | None = None


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content: str
    tags: list[str]
    metadata: dict = Field(validation_alias="metadata_", serialization_alias="metadata")
    created_at: datetime | None
    updated_at: datetime | None
