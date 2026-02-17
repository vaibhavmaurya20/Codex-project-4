from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from aegis_omega.common.config import SANDBOX_DIR, ensure_paths


@dataclass
class SandboxContext:
    sandbox_id: str
    root: Path
    workspace: Path
    logs: Path


class SandboxManager:
    """Creates per-task virtual Linux-like workspace rooted under ~/.aegis-omega/sandboxes."""

    def prepare(self, sandbox_id: str) -> SandboxContext:
        ensure_paths()
        root = SANDBOX_DIR / sandbox_id
        workspace = root / "workspace"
        logs = root / "logs"
        for p in (workspace, logs):
            p.mkdir(parents=True, exist_ok=True)
        self._seed_structure(root)
        return SandboxContext(sandbox_id=sandbox_id, root=root, workspace=workspace, logs=logs)

    @staticmethod
    def _seed_structure(root: Path) -> None:
        for rel in ("tmp", "etc", "var", "home", "opt", "usr/bin"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        marker = root / "etc" / "aegis-sandbox.conf"
        if not marker.exists():
            marker.write_text("mode=isolated-workspace\nnetwork=host\n")

    @staticmethod
    def environment(ctx: SandboxContext) -> dict[str, str]:
        env = os.environ.copy()
        env["AEGIS_SANDBOX_ID"] = ctx.sandbox_id
        env["AEGIS_SANDBOX_ROOT"] = str(ctx.root)
        env["HOME"] = str(ctx.root / "home")
        return env
