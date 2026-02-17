from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aegis_omega.common.config import MEMORY_DIR, RUNTIME_DIR, ensure_paths
from aegis_omega.common.models import Task


@dataclass
class MemoryRecord:
    key: str
    value: dict[str, Any]
    version: int = 1


@dataclass
class MemoryStore:
    short_term: dict[str, dict[str, Any]] = field(default_factory=dict)
    long_term: dict[str, dict[str, Any]] = field(default_factory=dict)
    failures: dict[str, dict[str, Any]] = field(default_factory=dict)
    tool_effectiveness: dict[str, dict[str, Any]] = field(default_factory=dict)

    def put(self, bucket: str, key: str, value: dict[str, Any]) -> None:
        target = getattr(self, bucket)
        current = target.get(key, {})
        version = int(current.get("version", 0)) + 1
        target[key] = asdict(MemoryRecord(key=key, value=value, version=version))

    def get(self, bucket: str, key: str) -> dict[str, Any] | None:
        return getattr(self, bucket).get(key)

    def persist(self) -> None:
        ensure_paths()
        payload = {
            "short_term": self.short_term,
            "long_term": self.long_term,
            "failures": self.failures,
            "tool_effectiveness": self.tool_effectiveness,
        }
        (MEMORY_DIR / "memory.json").write_text(json.dumps(payload, indent=2))

    @classmethod
    def restore(cls) -> "MemoryStore":
        ensure_paths()
        path = MEMORY_DIR / "memory.json"
        if not path.exists():
            return cls()
        payload = json.loads(path.read_text())
        return cls(**payload)


def append_audit_log(event: dict[str, Any]) -> None:
    ensure_paths()
    path = MEMORY_DIR / "audit.log"
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def persist_pending_tasks(tasks: list[Task]) -> None:
    ensure_paths()
    payload = [asdict(t) for t in tasks]
    (RUNTIME_DIR / "pending_tasks.json").write_text(json.dumps(payload, indent=2))


def restore_pending_tasks() -> list[Task]:
    ensure_paths()
    path = RUNTIME_DIR / "pending_tasks.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [Task(**item) for item in raw]
