"""
Document domain entity. Framework-independent, per W1 architecture.

Note on file storage (W7 spec, "IMPORTANT" section): real file upload /
cloud storage is explicitly out of scope for this phase. `storage_path` is
metadata only — a string the user (or a future upload feature) provides,
describing where the file lives (e.g. a local path). NEXUS does not read,
write, or serve the file's actual bytes. This is a deliberate limitation,
not a faked implementation — see the phase report, "Known issues".
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Document:
    title: str
    description: str = ""
    category: str = ""
    file_name: str = ""
    file_type: str = ""
    file_size: int | None = None
    storage_path: str = ""
    tags: list[str] = field(default_factory=list)
    expiry_date: date | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_expired(self, *, today: date) -> bool:
        return self.expiry_date is not None and self.expiry_date < today
