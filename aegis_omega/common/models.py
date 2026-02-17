from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TaskDomain(str, Enum):
    SOFTWARE = "software"
    LINUX_OS = "linux_os"
    CYBERSECURITY = "cybersecurity"
    RESEARCH = "research"
    DEVOPS = "devops"


@dataclass
class Task:
    id: str
    goal: str
    owner: str
    domain: TaskDomain = TaskDomain.SOFTWARE
    status: TaskStatus = TaskStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ActionRequest:
    task_id: str
    action: str
    command: str
    timeout_s: int = 120
    sandbox_id: str = "default"
    require_authorized_scope: bool = False


@dataclass
class ActionResult:
    task_id: str
    action: str
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    ended_at: str
    sandbox_id: str
