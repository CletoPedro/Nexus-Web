"""
User domain entity. Framework-independent, per W1 architecture. The
password hash lives here as an opaque string — hashing/verification logic
itself lives in app/security/hashing.py (infrastructure), never here.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    email: str
    hashed_password: str
    is_active: bool = True
    must_change_password: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None
