from __future__ import annotations

from dataclasses import dataclass, field

from aegis_omega.common.models import Task, TaskDomain


@dataclass
class Director:
    name: str
    memory_key: str
    domain: TaskDomain

    def spawn_worker_task(self, goal: str, sequence: int) -> Task:
        return Task(id=f"{self.name}-{sequence}", goal=goal, owner=self.name, domain=self.domain)


@dataclass
class AegisCoreGovernor:
    directors: dict[str, Director] = field(
        default_factory=lambda: {
            "software_architect_director": Director("software_architect_director", "software", TaskDomain.SOFTWARE),
            "linux_os_director": Director("linux_os_director", "linux", TaskDomain.LINUX_OS),
            "cybersecurity_director": Director("cybersecurity_director", "cyber", TaskDomain.CYBERSECURITY),
            "research_simulation_director": Director("research_simulation_director", "research", TaskDomain.RESEARCH),
            "devops_ci_director": Director("devops_ci_director", "devops", TaskDomain.DEVOPS),
        }
    )

    def assign(self, goal: str) -> Director:
        lowered = goal.lower()
        if "kernel" in lowered or "linux" in lowered or "driver" in lowered:
            return self.directors["linux_os_director"]
        if "security" in lowered or "vulnerability" in lowered or "pentest" in lowered:
            return self.directors["cybersecurity_director"]
        if "simulation" in lowered or "research" in lowered or "hypothesis" in lowered:
            return self.directors["research_simulation_director"]
        if "deploy" in lowered or "ci" in lowered or "pipeline" in lowered:
            return self.directors["devops_ci_director"]
        return self.directors["software_architect_director"]
