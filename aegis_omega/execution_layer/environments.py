from __future__ import annotations

import os
import subprocess
import threading
from pathlib import Path

from aegis_omega.common.config import SANDBOX_DIR, ensure_paths


class VirtualLinuxEnvironmentManager:
    """Creates isolated per-task working directories with optional Python virtualenv."""

    _lock = threading.Lock()

    def __init__(self) -> None:
        ensure_paths()

    def prepare(self, task_id: str) -> Path:
        root = SANDBOX_DIR / task_id
        with self._lock:
            (root / "workspace").mkdir(parents=True, exist_ok=True)
            (root / "logs").mkdir(parents=True, exist_ok=True)
            marker = root / ".venv_ready"
            if not marker.exists():
                subprocess.run(["python3", "-m", "venv", str(root / "venv")], check=False)
                marker.write_text("ok")
        return root

    def environment(self, root: Path) -> dict[str, str]:
        env = dict(os.environ)
        env["AEGIS_SANDBOX_ROOT"] = str(root)
        env["PATH"] = f"{root / 'venv' / 'bin'}:{env.get('PATH', '')}"
        env["PYTHONUNBUFFERED"] = "1"
        return env
