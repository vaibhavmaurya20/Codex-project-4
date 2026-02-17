from __future__ import annotations

import subprocess
from datetime import datetime, timezone

from aegis_omega.common.models import ActionRequest, ActionResult
from aegis_omega.execution_layer.environments import VirtualLinuxEnvironmentManager

SAFE_DENYLIST = ("rm -rf /", ":(){", "mkfs", "dd if=/dev/zero", "shutdown", "reboot")


class ExecutionLayer:
    """Execution only: runs commands in virtual Linux-like task sandboxes."""

    def __init__(self) -> None:
        self.env_manager = VirtualLinuxEnvironmentManager()

    def execute(self, request: ActionRequest) -> ActionResult:
        if any(token in request.command for token in SAFE_DENYLIST):
            return ActionResult(
                task_id=request.task_id,
                action=request.action,
                returncode=126,
                stdout="",
                stderr="Command blocked by safety policy",
                started_at=datetime.now(timezone.utc).isoformat(),
                ended_at=datetime.now(timezone.utc).isoformat(),
            )

        sandbox = self.env_manager.prepare(request.task_id)
        env = self.env_manager.environment(sandbox)
        started = datetime.now(timezone.utc).isoformat()
        proc = subprocess.run(
            request.command,
            shell=True,
            cwd=str(sandbox / "workspace"),
            capture_output=True,
            text=True,
            timeout=request.timeout_s,
            env=env,
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
        )
