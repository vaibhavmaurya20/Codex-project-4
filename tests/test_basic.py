from aegis_omega.autonomy_engine.planner import AutonomyEngine
from aegis_omega.common.config import AegisConfig
from aegis_omega.common.models import ActionRequest, Task
from aegis_omega.execution_layer.runner import ExecutionLayer


def test_goal_to_action_and_execution():
    brain = AutonomyEngine()
    task = Task(id="1", goal="hello world", owner="software_architect_director")
    requests = brain.evaluate_goals([task])
    assert requests

    result = ExecutionLayer(AegisConfig()).execute(requests[0])
    assert result.returncode == 0
    assert "planned step" in result.stdout
    assert result.sandbox_id == "1"


def test_safety_denylist():
    runner = ExecutionLayer(AegisConfig())
    req = ActionRequest(task_id="x", action="x", command="rm -rf /", timeout_s=1)
    result = runner.execute(req)
    assert result.returncode == 126


def test_security_scope_required_for_cyber_actions():
    runner = ExecutionLayer(AegisConfig(authorized_security_scopes=[]))
    req = ActionRequest(
        task_id="cyber-1",
        action="scan",
        command="echo test",
        timeout_s=1,
        require_authorized_scope=True,
    )
    result = runner.execute(req)
    assert result.returncode == 126
    assert "authorized security scope" in result.stderr
