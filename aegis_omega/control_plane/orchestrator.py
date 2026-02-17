from __future__ import annotations

import queue
import time
from dataclasses import dataclass, field
from typing import Iterable

from aegis_omega.common.models import Task, TaskStatus


@dataclass
class ControlPlane:
    task_queue: "queue.Queue[Task]" = field(default_factory=queue.Queue)
    scheduled: list[Task] = field(default_factory=list)

    def submit(self, task: Task) -> None:
        self.task_queue.put(task)

    def poll_events(self) -> list[Task]:
        events = []
        while not self.task_queue.empty():
            events.append(self.task_queue.get())
        return events

    def run_scheduled_tasks(self) -> Iterable[Task]:
        now = time.time()
        ready, waiting = [], []
        for task in self.scheduled:
            if float(task.metadata.get("run_at_epoch", 0)) <= now:
                ready.append(task)
            else:
                waiting.append(task)
        self.scheduled = waiting
        for task in ready:
            task.status = TaskStatus.PENDING
            yield task

    def schedule(self, task: Task, run_at_epoch: float) -> None:
        task.metadata["run_at_epoch"] = run_at_epoch
        self.scheduled.append(task)
