from __future__ import annotations

from dataclasses import dataclass

from aegis_omega.autonomy_engine.llm_router import MultiLLMRouter
from aegis_omega.common.models import ActionRequest, Task, TaskType


@dataclass
class AutonomyEngine:
    """Cognition only: generates plans and action requests without direct execution."""

    llm_router: MultiLLMRouter

    def evaluate_goals(self, tasks: list[Task]) -> list[ActionRequest]:
        actions: list[ActionRequest] = []
        for task in tasks:
            strategy_hints = self.llm_router.parallel_advice(task.goal, fanout=2)
            for idx, command in enumerate(self._goal_to_commands(task), start=1):
                hint = strategy_hints[(idx - 1) % len(strategy_hints)]["provider"]
                actions.append(
                    ActionRequest(
                        task_id=task.id,
                        action=f"step-{idx}:{hint}:{task.goal[:30]}",
                        command=command,
                        environment_profile="venv_linux",
                    )
                )
        return actions

    def detect_failures(self, results: list[dict]) -> list[str]:
        return [r["task_id"] for r in results if r.get("returncode", 1) != 0]

    def _goal_to_commands(self, task: Task) -> list[str]:
        safe_goal = task.goal.replace("\n", " ")[:180]
        common = [
            f"echo '[AEGIS] Goal: {safe_goal}'",
            "python -V",
        ]
        if task.task_type == TaskType.LINUX:
            return common + ["echo '[AEGIS] Linux workflow: configure -> build -> test in VM sandbox'"]
        if task.task_type == TaskType.CYBER_DEFENSE:
            return common + ["echo '[AEGIS] Cyber workflow: scope validation -> analysis -> mitigation report'"]
        if task.task_type == TaskType.RESEARCH:
            return common + ["echo '[AEGIS] Research workflow: ingest -> simulate -> analyze reproducibly'"]
        return common + ["echo '[AEGIS] Engineering workflow: design -> implement -> test -> package'"]
