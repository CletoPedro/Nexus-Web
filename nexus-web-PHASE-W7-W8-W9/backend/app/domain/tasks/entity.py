"""
Task domain entity. Per the W1 architecture, `domain/` never imports
FastAPI or SQLAlchemy — plain dataclass + enums only.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Status transitions considered valid business rules (W6 spec: "prevent
# invalid status transitions"). CANCELLED and DONE are terminal — a task
# can't be reopened by editing status directly; a new task should be
# created instead. This is a deliberate simplification for W6; a
# "reopen" affordance can be added later if needed.
_VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.DONE, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.TODO, TaskStatus.DONE, TaskStatus.CANCELLED},
    TaskStatus.DONE: set(),
    TaskStatus.CANCELLED: set(),
}


@dataclass
class Task:
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    completed_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_overdue(self, *, now: datetime) -> bool:
        return (
            self.due_date is not None
            and self.due_date < now
            and self.status not in (TaskStatus.DONE, TaskStatus.CANCELLED)
        )

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        if new_status == self.status:
            return True
        return new_status in _VALID_TRANSITIONS[self.status]
