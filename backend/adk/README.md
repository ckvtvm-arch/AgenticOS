# Agent Development Kit (ADK) — Quick Start

This folder contains a minimal ADK for developing and testing local agents.

Usage (from the `backend` directory with your virtualenv active):

Scaffold a new agent:

```bash
python -m adk.cli init my_agent
```

Run an agent file (wires decorated tools/handlers if present):

```bash
python -m adk.cli run agents/file_reader.py
```

Run tests in a sandbox (resource-limited subprocess):

```bash
python -m adk.cli test agents/some_agent_tests.py
```

Build a simple package (zip):

```bash
python -m adk.cli build agents/my_agent
```

See the `adk/sdk.py` for the `Agent` base class, `@tool`, and `@on_message` decorators.
