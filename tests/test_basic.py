from aegis_omega.autonomy_engine.llm_router import MultiLLMRouter
from aegis_omega.autonomy_engine.planner import AutonomyEngine
from aegis_omega.common.models import ActionRequest, Task
from aegis_omega.execution_layer.runner import ExecutionLayer


def test_goal_to_action_and_execution():
    brain = AutonomyEngine(llm_router=MultiLLMRouter(["local_fallback"]))
    task = Task(id="1", goal="hello world", owner="software_architect_director")
    requests = brain.evaluate_goals([task])
    assert requests

    result = ExecutionLayer().execute(requests[0])
    assert result.returncode == 0
    assert "[AEGIS] Goal" in result.stdout


def test_safety_denylist():
    runner = ExecutionLayer()
    req = ActionRequest(task_id="x", action="x", command="rm -rf /", timeout_s=1)
    result = runner.execute(req)
    assert result.returncode == 126


def test_parallel_advice():
    router = MultiLLMRouter(["a", "b", "c"])
    responses = router.parallel_advice("make a plan", fanout=2)
    assert len(responses) == 2
    assert all("provider" in r for r in responses)
