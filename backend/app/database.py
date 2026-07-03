import json
import os
from typing import Any, Dict, List

from sqlalchemy import Column, Integer, String, Text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agenticos.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class AgentRecord(Base):
    """Persisted agent registration, so the registry survives a backend restart."""

    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    script_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer, default=50)
    capabilities = Column(Text, default="[]")
    metadata_json = Column(Text, default="{}")
    cpu_quota_seconds = Column(Integer, default=20)
    max_retries = Column(Integer, default=3)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session


async def load_agents() -> List[Dict[str, Any]]:
    """Restore previously registered agents on startup."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AgentRecord))
        return [
            {
                "id": r.id,
                "name": r.name,
                "script_name": r.script_name,
                "status": r.status,
                "priority": r.priority,
                "capabilities": json.loads(r.capabilities or "[]"),
                "metadata": json.loads(r.metadata_json or "{}"),
                "cpu_quota_seconds": r.cpu_quota_seconds,
                "max_retries": r.max_retries,
            }
            for r in result.scalars().all()
        ]


async def upsert_agents(agents: List[Dict[str, Any]]) -> None:
    """Snapshot current registry state so a restart can recover it."""
    async with AsyncSessionLocal() as session:
        for agent in agents:
            record = await session.get(AgentRecord, agent["id"])
            if record is None:
                record = AgentRecord(id=agent["id"])
                session.add(record)
            record.name = agent["name"]
            record.script_name = agent["script_name"]
            record.status = agent["status"]
            record.priority = agent["priority"]
            record.capabilities = json.dumps(agent["capabilities"])
            record.metadata_json = json.dumps(agent["metadata"])
        await session.commit()


async def delete_agent_record(agent_id: str) -> None:
    async with AsyncSessionLocal() as session:
        record = await session.get(AgentRecord, agent_id)
        if record:
            await session.delete(record)
            await session.commit()