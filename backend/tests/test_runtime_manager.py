from app.models import AgentStatus
from app.runtime.manager import AgentProcess, Scheduler


def test_needs_restart_true_for_unexpected_crash():
    agent = AgentProcess(id="a1", name="a", script_name="hello_agent.py")
    agent.status = AgentStatus.Terminated
    agent.manual_stop = False
    agent.retries = 0
    agent.max_retries = 3
    assert agent.needs_restart() is True


def test_needs_restart_false_after_manual_terminate():
    agent = AgentProcess(id="a1", name="a", script_name="hello_agent.py")
    agent.terminate(manual=True)
    assert agent.status == AgentStatus.Terminated
    assert agent.manual_stop is True
    assert agent.needs_restart() is False


def test_needs_restart_false_once_retry_budget_exhausted():
    agent = AgentProcess(id="a1", name="a", script_name="hello_agent.py")
    agent.status = AgentStatus.Terminated
    agent.manual_stop = False
    agent.retries = 3
    agent.max_retries = 3
    assert agent.needs_restart() is False


def test_action_terminate_is_not_auto_restarted(registry):
    agent = registry.register_agent(name="t1", script_name="hello_agent.py")
    assert agent.is_alive()

    agent.terminate(manual=True)

    assert agent.status == AgentStatus.Terminated
    assert agent.needs_restart() is False


def test_pause_is_not_auto_resumed_by_scheduler(registry):
    agent = registry.register_agent(name="t2", script_name="hello_agent.py")
    scheduler = Scheduler(registry, max_running=3)

    agent.pause()
    assert agent.status == AgentStatus.Paused

    scheduler.schedule()

    assert agent.status == AgentStatus.Paused

    agent.resume()
    assert agent.status == AgentStatus.Running


def test_scheduler_does_not_resume_paused_agent_when_capacity_frees(registry):
    scheduler = Scheduler(registry, max_running=1)

    running_agent = registry.register_agent(name="occupies-slot", script_name="hello_agent.py")
    paused_agent = registry.register_agent(name="paused", script_name="hello_agent.py")
    paused_agent.pause()

    running_agent.terminate(manual=True)
    scheduler.schedule()

    assert paused_agent.status == AgentStatus.Paused


def test_scheduler_spawns_queued_idle_agent_when_capacity_frees(registry):
    scheduler = Scheduler(registry, max_running=1)

    running_agent = registry.register_agent(name="occupies-slot", script_name="hello_agent.py")
    queued_agent = registry.register_agent(name="queued", script_name="hello_agent.py", spawn_now=False)
    assert queued_agent.status == AgentStatus.Idle

    scheduler.schedule()
    assert queued_agent.status == AgentStatus.Idle

    running_agent.terminate(manual=True)
    scheduler.schedule()

    assert queued_agent.status == AgentStatus.Running
    assert queued_agent.is_alive()
