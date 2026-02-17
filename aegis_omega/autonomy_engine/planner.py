from __future__ import annotations

from dataclasses import dataclass

from aegis_omega.autonomy_engine.model_router import ModelRouter
from aegis_omega.common.models import ActionRequest, Task, TaskDomain


@dataclass
class AutonomyEngine:
    """Cognition-only planner with decomposition and parallel-model advisory."""

    router: ModelRouter = ModelRouter()

    def evaluate_goals(self, tasks: list[Task]) -> list[ActionRequest]:
        actions: list[ActionRequest] = []
        for task in tasks:
            steps = self.decompose_goal(task)
            for idx, step in enumerate(steps, start=1):
                command = self._goal_to_safe_command(step)
                actions.append(
                    ActionRequest(
                        task_id=f"{task.id}-s{idx}",
                        action=f"execute:{step}",
                        command=command,
                        sandbox_id=task.id,
                        require_authorized_scope=task.domain == TaskDomain.CYBERSECURITY,
                    )
                )
        return actions

    def detect_failures(self, results: list[dict]) -> list[str]:
        return [r["task_id"] for r in results if r.get("returncode", 1) != 0]

    def decompose_goal(self, task: Task) -> list[str]:
        advisory = self.router.ask_parallel(task.goal)
        _ = advisory  # preserves low-resource behavior while allowing future ranking logic.

        common = [
            f"analyze goal requirements for {task.goal}",
            f"implement and execute deliverables for {task.goal}",
            f"run validation and summarize outcomes for {task.goal}",
        ]
        if task.domain == TaskDomain.CYBERSECURITY:
            return [
                f"validate authorization scope for {task.goal}",
                f"perform passive vulnerability analysis for {task.goal}",
                f"generate mitigations and patch guidance for {task.goal}",
            ]
        if task.domain == TaskDomain.LINUX_OS:
            return [
                f"prepare isolated linux build workspace for {task.goal}",
                f"run build or module workflow for {task.goal}",
                f"collect boot or compile diagnostics for {task.goal}",
            ]
        return common

    @staticmethod
    def _goal_to_safe_command(goal: str) -> str:
        sanitized = goal.replace("\n", " ")[:120]
        return f"echo '[AEGIS] planned step: {sanitized}'"
