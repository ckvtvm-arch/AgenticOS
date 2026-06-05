from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

import psutil

from ..models import AgentStatus, Resource, ResourceType, SystemService, SystemServiceStatus

DEFAULT_MAX_RETRIES = 3
DEFAULT_HEARTBEAT_TIMEOUT = 15
DEFAULT_MONITOR_INTERVAL = 2
DEFAULT_MAX_RUNNING = 3

@dataclass
class AgentProcess:
    id: str
    name: str
    script_name: str
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    priority: int = 50
    cpu_quota_seconds: int = 20
    status: AgentStatus = AgentStatus.Idle
    pid: Optional[int] = None
    process: Optional[subprocess.Popen] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    heartbeat_at: Optional[datetime] = None
    retries: int = 0
    max_retries: int = DEFAULT_MAX_RETRIES
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    _proc_handle: Optional[psutil.Process] = None

    @property
    def script_path(self) -> Path:
        return Path(__file__).resolve().parents[2] / 'agents' / self.script_name

    def _preexec_fn(self):
        if self.cpu_quota_seconds and self.cpu_quota_seconds > 0:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_quota_seconds, self.cpu_quota_seconds))

    def spawn(self, backend_url: str) -> None:
        if self.process and self.is_alive():
            return

        if not self.script_path.exists():
            raise FileNotFoundError(f"Agent script not found: {self.script_path}")

        env = os.environ.copy()
        env.update({
            'AGENT_ID': self.id,
            'AGENT_NAME': self.name,
            'BACKEND_URL': backend_url,
            'AGENT_CAPABILITIES': json.dumps(self.capabilities),
            'AGENT_METADATA': json.dumps(self.metadata),
        })

        self.process = subprocess.Popen(
            [sys.executable, str(self.script_path)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=self._preexec_fn,
        )

        self.pid = self.process.pid
        self.status = AgentStatus.Running
        self.started_at = datetime.utcnow()
        self.heartbeat_at = datetime.utcnow()
        self._proc_handle = psutil.Process(self.pid)
        self.cpu_percent = 0.0
        self.memory_mb = 0.0

    def pause(self) -> None:
        if self.is_alive() and self.pid:
            os.kill(self.pid, signal.SIGSTOP)
            self.status = AgentStatus.Paused

    def resume(self) -> None:
        if self.is_alive() and self.pid:
            os.kill(self.pid, signal.SIGCONT)
            self.status = AgentStatus.Running

    def terminate(self) -> None:
        if self.process and self.is_alive():
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.status = AgentStatus.Terminated
        self.terminated_at = datetime.utcnow()
        self.pid = None
        self._proc_handle = None

    def is_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def update_metrics(self) -> None:
        if self.pid is None:
            self.cpu_percent = 0.0
            self.memory_mb = 0.0
            return

        try:
            self._proc_handle = self._proc_handle or psutil.Process(self.pid)
            self.cpu_percent = self._proc_handle.cpu_percent(interval=None)
            self.memory_mb = self._proc_handle.memory_info().rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.cpu_percent = 0.0
            self.memory_mb = 0.0

    def needs_restart(self) -> bool:
        if self.status == AgentStatus.Terminated:
            return self.retries < self.max_retries
        if self.heartbeat_at is None:
            return False
        return (datetime.utcnow() - self.heartbeat_at) > timedelta(seconds=DEFAULT_HEARTBEAT_TIMEOUT)

    def restart(self, backend_url: str) -> None:
        if self.retries >= self.max_retries:
            self.status = AgentStatus.Terminated
            return

        self.terminate()
        self.retries += 1
        self.spawn(backend_url)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'script_name': self.script_name,
            'pid': self.pid,
            'priority': self.priority,
            'capabilities': self.capabilities,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'terminated_at': self.terminated_at.isoformat() if self.terminated_at else None,
            'heartbeat_at': self.heartbeat_at.isoformat() if self.heartbeat_at else None,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
        }


class AgentRegistry:
    def __init__(self, backend_url: str):
        self.agents: Dict[str, AgentProcess] = {}
        self.backend_url = backend_url
        self._on_change: Optional[Callable[[], None]] = None

    def set_update_callback(self, callback: Callable[[], None]) -> None:
        self._on_change = callback

    def _trigger_update(self) -> None:
        if self._on_change:
            self._on_change()

    def register_agent(
        self,
        name: str,
        script_name: str,
        priority: int = 50,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        cpu_quota_seconds: int = 20,
        spawn_now: bool = True,
    ) -> AgentProcess:
        agent_id = f"agent-{len(self.agents) + 1:03d}"
        agent = AgentProcess(
            id=agent_id,
            name=name,
            script_name=script_name,
            priority=priority,
            capabilities=capabilities or [],
            metadata=metadata or {},
            cpu_quota_seconds=cpu_quota_seconds,
        )
        self.agents[agent_id] = agent
        if spawn_now:
            agent.spawn(self.backend_url)
        self._trigger_update()
        return agent

    def deregister_agent(self, agent_id: str) -> None:
        agent = self.agents.get(agent_id)
        if agent:
            agent.terminate()
            del self.agents[agent_id]
            self._trigger_update()

    def get_agent(self, agent_id: str) -> Optional[AgentProcess]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[AgentProcess]:
        return list(self.agents.values())

    def discover(self, capability: str) -> List[AgentProcess]:
        return [agent for agent in self.agents.values() if capability in agent.capabilities]

    def heartbeat(self, agent_id: str) -> Optional[AgentProcess]:
        agent = self.agents.get(agent_id)
        if agent:
            agent.heartbeat_at = datetime.utcnow()
            if agent.status == AgentStatus.Idle:
                agent.status = AgentStatus.Running
            self._trigger_update()
        return agent

    def update_metrics(self) -> None:
        for agent in self.agents.values():
            agent.update_metrics()

    def get_system_resources(self) -> List[Resource]:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        return [
            Resource(type=ResourceType.CPU, usage=cpu, total=os.cpu_count() or 1, unit='Cores'),
            Resource(type=ResourceType.GPU, usage=0.0, total=0, unit='GB VRAM'),
            Resource(type=ResourceType.Memory, usage=100 * (mem.total - mem.available) / mem.total, total=round(mem.total / (1024 ** 3)), unit='GB RAM'),
            Resource(type=ResourceType.TokenBudget, usage=65.0, total=1000000, unit='Tokens/hr'),
        ]

    def get_service_statuses(self) -> List[SystemService]:
        return [
            SystemService(name='Agent Registry', status=SystemServiceStatus.Online),
            SystemService(name='Inference Engine', status=SystemServiceStatus.Online),
            SystemService(name='Context Management', status=SystemServiceStatus.Degraded),
            SystemService(name='Tool Execution', status=SystemServiceStatus.Online),
            SystemService(name='Communication Bus', status=SystemServiceStatus.Offline),
        ]

    async def monitor_loop(self) -> None:
        while True:
            self.update_metrics()
            for agent in self.agents.values():
                if agent.needs_restart():
                    agent.restart(self.backend_url)
                    self._trigger_update()

            self._trigger_update()
            await asyncio.sleep(DEFAULT_MONITOR_INTERVAL)


class Scheduler:
    def __init__(self, registry: AgentRegistry, max_running: int = DEFAULT_MAX_RUNNING):
        self.registry = registry
        self.max_running = max_running

    def schedule(self) -> None:
        running = [agent for agent in self.registry.list_agents() if agent.status == AgentStatus.Running and agent.is_alive()]
        if len(running) >= self.max_running:
            return

        idle_agents = [agent for agent in self.registry.list_agents() if agent.status in {AgentStatus.Idle, AgentStatus.Paused}]
        if not idle_agents:
            return

        idle_agents.sort(key=lambda a: (a.priority, a.created_at))
        next_agent = idle_agents[0]
        if next_agent.status == AgentStatus.Idle:
            next_agent.spawn(self.registry.backend_url)
        else:
            next_agent.resume()
        self.registry._trigger_update()


class RuntimeManager:
    def __init__(self, backend_url: str):
        self.registry = AgentRegistry(backend_url)
        self.scheduler = Scheduler(self.registry)
        self.update_callback: Optional[Callable[[], None]] = None

    def set_update_callback(self, callback: Callable[[], None]) -> None:
        self.update_callback = callback
        self.registry.set_update_callback(callback)

    def register_agent(self, **kwargs) -> AgentProcess:
        return self.registry.register_agent(**kwargs)

    def get_agent(self, agent_id: str) -> Optional[AgentProcess]:
        return self.registry.get_agent(agent_id)

    def list_agents(self) -> List[Dict]:
        return [agent.to_dict() for agent in self.registry.list_agents()]

    def heartbeat(self, agent_id: str) -> Optional[Dict]:
        agent = self.registry.heartbeat(agent_id)
        return agent.to_dict() if agent else None

    def action(self, agent_id: str, action: AgentStatus) -> Optional[Dict]:
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return None
        if action == AgentStatus.Paused:
            agent.pause()
        elif action == AgentStatus.Running:
            if agent.status == AgentStatus.Paused:
                agent.resume()
            elif not agent.is_alive():
                agent.spawn(self.registry.backend_url)
        elif action == AgentStatus.Terminated:
            agent.terminate()
        self.registry._trigger_update()
        return agent.to_dict()

    def get_resources(self) -> List[Resource]:
        return self.registry.get_system_resources()

    def get_services(self) -> List[SystemService]:
        return self.registry.get_service_statuses()

    def discover(self, capability: str) -> List[Dict]:
        return [agent.to_dict() for agent in self.registry.discover(capability)]

    async def start(self) -> None:
        asyncio.create_task(self.registry.monitor_loop())
        asyncio.create_task(self._scheduler_loop())

    async def _scheduler_loop(self) -> None:
        while True:
            self.scheduler.schedule()
            await asyncio.sleep(DEFAULT_MONITOR_INTERVAL)
