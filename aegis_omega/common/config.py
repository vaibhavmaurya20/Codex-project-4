from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path.home() / ".aegis-omega"
RUNTIME_DIR = BASE_DIR / "runtime"
LOG_DIR = BASE_DIR / "logs"
MEMORY_DIR = BASE_DIR / "memory"
SANDBOX_DIR = BASE_DIR / "sandboxes"
CONFIG_FILE = BASE_DIR / "config.json"


@dataclass
class AegisConfig:
    loop_interval_s: int = 5
    max_workers: int = 4
    enable_cloud_models: bool = False
    enable_docker_execution: bool = False
    lightweight_mode: bool = True
    allow_live_terminal: bool = False
    authorized_security_scopes: list[str] = field(default_factory=list)
    auto_recovery: bool = True


def ensure_paths() -> None:
    for p in (BASE_DIR, RUNTIME_DIR, LOG_DIR, MEMORY_DIR, SANDBOX_DIR):
        p.mkdir(parents=True, exist_ok=True)


def load_config() -> AegisConfig:
    ensure_paths()
    if not CONFIG_FILE.exists():
        cfg = AegisConfig()
        save_config(cfg)
        return cfg
    data = json.loads(CONFIG_FILE.read_text())
    return AegisConfig(**data)


def save_config(cfg: AegisConfig) -> None:
    ensure_paths()
    CONFIG_FILE.write_text(json.dumps(cfg.__dict__, indent=2))
