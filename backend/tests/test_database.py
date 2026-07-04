import asyncio

from app.database import delete_agent_record, init_db, load_agents, upsert_agents


def run(coro):
    return asyncio.run(coro)


def make_agent(agent_id, status="Running"):
    return {
        "id": agent_id,
        "name": "TestAgent",
        "script_name": "hello_agent.py",
        "status": status,
        "priority": 10,
        "capabilities": ["test"],
        "metadata": {"k": "v"},
        "cpu_quota_seconds": 20,
        "max_retries": 3,
    }


def test_upsert_then_load_round_trip():
    run(init_db())
    run(upsert_agents([make_agent("test-agent-001")]))

    loaded = run(load_agents())
    match = next(a for a in loaded if a["id"] == "test-agent-001")
    assert match["name"] == "TestAgent"
    assert match["status"] == "Running"
    assert match["capabilities"] == ["test"]
    assert match["metadata"] == {"k": "v"}


def test_upsert_updates_existing_record_instead_of_duplicating():
    run(init_db())
    agent = make_agent("test-agent-002", status="Running")
    run(upsert_agents([agent]))

    agent["status"] = "Terminated"
    run(upsert_agents([agent]))

    loaded = run(load_agents())
    matches = [a for a in loaded if a["id"] == "test-agent-002"]
    assert len(matches) == 1
    assert matches[0]["status"] == "Terminated"


def test_delete_agent_record_removes_row():
    run(init_db())
    run(upsert_agents([make_agent("test-agent-003")]))
    run(delete_agent_record("test-agent-003"))

    loaded = run(load_agents())
    assert all(a["id"] != "test-agent-003" for a in loaded)
