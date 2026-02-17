from __future__ import annotations

import argparse
import json
import signal
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from aegis_omega.agents.governance import AegisCoreGovernor
from aegis_omega.autonomy_engine.llm_router import MultiLLMRouter
from aegis_omega.autonomy_engine.planner import AutonomyEngine
from aegis_omega.common.config import RUNTIME_DIR, ensure_paths, load_config
from aegis_omega.common.models import Task, TaskStatus
from aegis_omega.control_plane.orchestrator import ControlPlane
from aegis_omega.execution_layer.runner import ExecutionLayer
from aegis_omega.memory.store import (
    MemoryStore,
    append_audit_log,
    persist_pending_tasks,
    restore_pending_tasks,
)

alive = True


def _stop(*_: object) -> None:
    global alive
    alive = False


def run(seed_goals: list[str]) -> None:
    ensure_paths()
    cfg = load_config()
    memory = MemoryStore.restore()
    plane = ControlPlane()
    llm_router = MultiLLMRouter(providers=cfg.llm_providers)
    brain = AutonomyEngine(llm_router=llm_router)
    exec_layer = ExecutionLayer()
    governor = AegisCoreGovernor()

    restored = restore_pending_tasks()
    for task in restored:
        plane.submit(task)

    for idx, goal in enumerate(seed_goals, start=1):
        director = governor.assign(goal)
        plane.submit(director.spawn_worker_task(goal=goal, sequence=idx))

    state_file = RUNTIME_DIR / "state.json"

    while alive:
        tasks = plane.poll_events() + list(plane.run_scheduled_tasks())
        persist_pending_tasks(tasks)
        requests = brain.evaluate_goals(tasks)

        with ThreadPoolExecutor(max_workers=max(1, cfg.max_parallel_agents)) as pool:
            results = [asdict(r) for r in pool.map(exec_layer.execute, requests)]

        failed_ids = set(brain.detect_failures(results))
        for task in tasks:
            if task.id in failed_ids:
                plane.mark_failure(task)
                memory.put("failures", task.id, {"reason": "non-zero exit", "retries": task.retries})
            else:
                task.status = TaskStatus.DONE
                memory.put("tool_effectiveness", task.owner, {"task_id": task.id, "score": 0.9})

        for res in results:
            memory.put("short_term", f"{res['task_id']}:{res['action']}", res)
            append_audit_log({"type": "execution_result", "payload": res})

        memory.put(
            "long_term",
            "self_improvement_hook",
            {
                "action": "collect_metrics_and_re-rank_providers",
                "providers": cfg.llm_providers,
                "timestamp": time.time(),
            },
        )
        memory.persist()
        state_file.write_text(
            json.dumps(
                {
                    "alive": alive,
                    "tasks_polled": len(tasks),
                    "results": len(results),
                    "dead_letter": len(plane.dead_letter),
                },
                indent=2,
            )
        )
        time.sleep(cfg.loop_interval_s)


def main() -> None:
    parser = argparse.ArgumentParser(description="AEGIS-Ω v2.1")
    parser.add_argument("--goal", action="append", default=[], help="Seed goals for the always-on loop")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    run(args.goal or ["maintain autonomous operations"])


if __name__ == "__main__":
    main()
