from __future__ import annotations

import argparse
import json
import signal
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from aegis_omega.agents.governance import AegisCoreGovernor
from aegis_omega.autonomy_engine.planner import AutonomyEngine
from aegis_omega.common.config import RUNTIME_DIR, ensure_paths, load_config
from aegis_omega.common.models import Task
from aegis_omega.control_plane.orchestrator import ControlPlane
from aegis_omega.execution_layer.runner import ExecutionLayer
from aegis_omega.memory.store import MemoryStore, append_audit_log

alive = True


def _stop(*_: object) -> None:
    global alive
    alive = False


def _execute_parallel(exec_layer: ExecutionLayer, requests: list) -> list[dict]:
    if not requests:
        return []
    with ThreadPoolExecutor(max_workers=max(1, min(len(requests), exec_layer.cfg.max_workers))) as pool:
        return [asdict(result) for result in pool.map(exec_layer.execute, requests)]


def run(seed_goals: list[str]) -> None:
    ensure_paths()
    cfg = load_config()
    memory = MemoryStore.restore()
    plane = ControlPlane()
    brain = AutonomyEngine()
    exec_layer = ExecutionLayer(cfg)
    governor = AegisCoreGovernor()

    for idx, goal in enumerate(seed_goals, start=1):
        director = governor.assign(goal)
        plane.submit(director.spawn_worker_task(goal=goal, sequence=idx))

    state_file = RUNTIME_DIR / "state.json"

    while alive:
        tasks = plane.poll_events() + list(plane.run_scheduled_tasks())
        requests = brain.evaluate_goals(tasks)
        results = _execute_parallel(exec_layer, requests)

        for res in results:
            memory.put("short_term", res["task_id"], res)
            append_audit_log({"type": "execution_result", "payload": res})

        failed_ids = brain.detect_failures(results)
        for failed_id in failed_ids:
            recovery = {"reason": "non-zero exit", "recoverable": cfg.auto_recovery}
            memory.put("failures", failed_id, recovery)
            if cfg.auto_recovery:
                plane.submit(Task(id=f"recover-{failed_id}", goal=f"recover task {failed_id}", owner="aegis_core"))

        memory.persist()
        state_file.write_text(
            json.dumps(
                {
                    "alive": alive,
                    "tasks_polled": len(tasks),
                    "requests": len(requests),
                    "results": len(results),
                    "failures": len(failed_ids),
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
