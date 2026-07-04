import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).resolve().parent / "test_agenticos.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

import pytest

from app.runtime.manager import AgentRegistry

FAKE_BACKEND_URL = "http://127.0.0.1:1"


@pytest.fixture
def registry():
    reg = AgentRegistry(backend_url=FAKE_BACKEND_URL)
    yield reg
    for agent in reg.list_agents():
        agent.terminate()


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db():
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
