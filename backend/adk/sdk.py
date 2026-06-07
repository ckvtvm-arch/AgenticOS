from __future__ import annotations

import inspect
import threading
import time
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str = "unnamed-agent"
    id: Optional[str] = None
    backend_url: Optional[str] = None


class Agent:
    """Base Agent class for ADK.

    Subclass `Agent` and override lifecycle hooks as needed.
    Tools can be registered using the `@tool` decorator.
    """

    def __init__(self, config: AgentConfig | dict | None = None):
        if config is None:
            config = {}
        if isinstance(config, dict):
            config = AgentConfig(**config)
        self.config: AgentConfig = config
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._message_handler: Optional[Callable[[str, dict], Any]] = None
        self._running = False

    # Lifecycle hooks
    def on_start(self, config: AgentConfig) -> None:
        return None

    def on_pause(self) -> None:
        return None

    def on_resume(self) -> None:
        return None

    def on_terminate(self) -> None:
        return None

    def register_tool(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def tools(self) -> Dict[str, Callable[..., Any]]:
        return dict(self._tools)

    def set_message_handler(self, fn: Callable[[str, dict], Any]) -> None:
        self._message_handler = fn

    def handle_message(self, sender: str, payload: dict) -> Any:
        if self._message_handler:
            return self._message_handler(sender, payload)
        raise RuntimeError("No message handler registered")

    # Basic run loop for local development
    def run(self) -> None:
        self._running = True
        try:
            self.on_start(self.config)
            while self._running:
                time.sleep(0.1)
        finally:
            self.on_terminate()

    def stop(self) -> None:
        self._running = False


def tool(fn: Callable[..., Any] | None = None, *, name: Optional[str] = None):
    """Decorator to mark a callable as a tool for the agent.

    Usage:
        @tool
        def compute(x):
            return x*2
    """

    def decorator(func: Callable[..., Any]):
        func._is_tool = True  # type: ignore[attr-defined]
        func._tool_name = name or func.__name__  # type: ignore[attr-defined]
        return func

    if fn is None:
        return decorator
    return decorator(fn)


def on_message(fn: Callable[[str, dict], Any]):
    """Decorator to register an agent message handler.

    Usage:
        @on_message
        def handler(sender, payload):
            ...
    """

    fn._is_message_handler = True  # type: ignore[attr-defined]
    return fn


def discover_tools(module) -> Dict[str, Callable[..., Any]]:
    tools: Dict[str, Callable[..., Any]] = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and getattr(obj, "_is_tool", False):
            tools[getattr(obj, "_tool_name", name)] = obj
    return tools


def attach_decorated_to_agent(agent: Agent, module) -> None:
    """Attach functions decorated with @tool and @on_message from a module to an Agent."""
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and getattr(obj, "_is_tool", False):
            tool_name = getattr(obj, "_tool_name", name)
            agent.register_tool(tool_name, obj)
        if inspect.isfunction(obj) and getattr(obj, "_is_message_handler", False):
            agent.set_message_handler(obj)

