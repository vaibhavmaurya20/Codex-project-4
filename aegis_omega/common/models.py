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


class TaskType(str, Enum):
    SOFTWARE = "software"
    LINUX = "linux"
    CYBER_DEFENSE = "cyber_defense"
    RESEARCH = "research"
    DEVOPS = "devops"
    GENERAL = "general"


@dataclass
class Task:
    id: str
    goal: str
    owner: str
    task_type: TaskType = TaskType.GENERAL
    status: TaskStatus = TaskStatus.PENDING
    retries: int = 0
    max_retries: int = 2
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ActionRequest:
    task_id: str
    action: str
    command: str
    environment_profile: str = "venv_linux"
    timeout_s: int = 300


@dataclass
class ActionResult:
    task_id: str
    action: str
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    ended_at: str
