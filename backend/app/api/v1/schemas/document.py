"""Pydantic schemas for the Document API."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=10_000)
    category: str = Field(default="", max_length=100)
    file_name: str = Field(default="", max_length=500)
    file_type: str = Field(default="", max_length=100)
    file_size: int | None = None
    storage_path: str = Field(
        default="",
        max_length=2000,
        description=(
            "Metadata only — e.g. a local file path the user provides. "
            "NEXUS does not store or serve the file's actual bytes (no "
            "upload/cloud storage in this phase)."
        ),
    )
    tags: list[str] = Field(default_factory=list)
    expiry_date: date | None = None


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10_000)
    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    expiry_date: date | None = None
    expiry_date_provided: bool = False


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    category: str
    file_name: str
    file_type: str
    file_size: int | None
    storage_path: str
    tags: list[str]
    expiry_date: date | None
    created_at: datetime | None
    updated_at: datetime | None
