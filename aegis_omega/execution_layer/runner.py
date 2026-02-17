from __future__ import annotations

import subprocess
from datetime import datetime, timezone

from aegis_omega.common.config import AegisConfig
from aegis_omega.common.models import ActionRequest, ActionResult
from aegis_omega.execution_layer.sandbox import SandboxManager

SAFE_DENYLIST = ("rm -rf /", ":(){", "mkfs", "dd if=/dev/zero")


class ExecutionLayer:
    """Execution only: runs commands in per-task virtualized workspace directories."""

    def __init__(self, cfg: AegisConfig) -> None:
        self.cfg = cfg
        self.sandbox = SandboxManager()

    def execute(self, request: ActionRequest) -> ActionResult:
        if any(token in request.command for token in SAFE_DENYLIST):
            return self._blocked_result(request, "Command blocked by safety policy")

        if request.require_authorized_scope and not self.cfg.authorized_security_scopes:
            return self._blocked_result(request, "No authorized security scope configured")

        ctx = self.sandbox.prepare(request.sandbox_id)
        started = datetime.now(timezone.utc).isoformat()
        proc = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=request.timeout_s,
            cwd=ctx.workspace,
            env=self.sandbox.environment(ctx),
        )
        ended = datetime.now(timezone.utc).isoformat()
        return ActionResult(
            task_id=request.task_id,
            action=request.action,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            started_at=started,
            ended_at=ended,
            sandbox_id=request.sandbox_id,
        )

    @staticmethod
    def _blocked_result(request: ActionRequest, reason: str) -> ActionResult:
        now = datetime.now(timezone.utc).isoformat()
        return ActionResult(
            task_id=request.task_id,
            action=request.action,
            returncode=126,
            stdout="",
            stderr=reason,
            started_at=now,
            ended_at=now,
            sandbox_id=request.sandbox_id,
        )
