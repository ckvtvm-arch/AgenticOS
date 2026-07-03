# AgenticOS Roadmap

> **Last updated:** May 2026

---

## Phase 0: Foundation — Documentation & Structure (Current)

**Goal:** Establish project conventions, architecture blueprint, and contributor infrastructure.

| Milestone | Acceptance Criteria | Effort |
|-----------|-------------------|--------|
| `ARCHITECTURE.md` | Documents layers, components, data flow, tech choices | Done |
| `ROADMAP.md` | Phased milestones with clear acceptance criteria | Done |
| `CONTRIBUTING.md` | Setup guide, code conventions, PR workflow | Done |
| `README.md` updated | Links to all new docs | 1 day |
| GitHub Issues template | Bug report + feature request templates | 1 day |
| CI pipeline | Lint + type-check + test on push | 2 days |

**Timeline:** 1 week

---

## Phase 1: Backend API & Dashboard Integration (MVP-1)

**Goal:** Replace mock data with a real FastAPI backend. Dashboard shows live data.

### Milestone 1.1 — FastAPI Server
- `GET /api/agents` — list agents with status + resource usage
- `GET /api/resources` — system CPU, GPU, memory, token metrics
- `GET /api/services` — system service health
- `POST /api/agents` — spawn a new agent
- `POST /api/agents/{id}/action` — pause / resume / terminate
- WebSocket endpoint for real-time streaming updates
- SQLite database for persistence

### Milestone 1.2 — Dashboard Rewire
- Replace all `useState` mock data with `fetch()` calls
- WebSocket subscription for live updates (replace 2s interval)
- Loading states, error boundaries, reconnection handling
- Remove `useEffect` simulation logic

### Milestone 1.3 — Docker Compose Dev Environment
- `docker-compose.yml` with backend + dashboard services
- Volume mounts for hot reload
- Environment variable configuration

**Timeline:** 2–3 weeks
**Dependencies:** Phase 0

---

## Phase 2: Agent Runtime & Lifecycle (MVP-2)

**Goal:** Actually spawn, manage, and monitor real agent processes.

### Milestone 2.1 — Process Manager
- Spawn agent processes (Python subprocesses initially)
- Track PID, status, resource usage per agent
- Health check pings (heartbeat mechanism)
- Clean termination with timeout + force-kill fallback

### Milestone 2.2 — Agent Scheduler (Basic)
- Priority queue-based scheduling
- Pause/resume via signal (SIGSTOP/SIGCONT)
- CPU quota enforcement (resource limits via `cgroups`/`prlimit`)

### Milestone 2.3 — Agent Registry
- Register/deregister agents
- Capability discovery endpoint
- Heartbeat monitoring with automatic restart (max 3 retries)
- Agent metadata (version, author, dependencies)

**Timeline:** 4–6 weeks
**Dependencies:** Phase 1

---

## Phase 3: Agent Development Kit (ADK)

**Goal:** Developers can build and test agents locally.

### Milestone 3.1 — Python SDK
- `Agent` base class with lifecycle hooks
  - `on_start(config)` — called when agent spawns
  - `on_pause()` — called before suspension
  - `on_resume()` — called after resume
  - `on_terminate()` — cleanup before shutdown
- `@tool` decorator for registering callable functions
- `@agent.on_message` handler for inter-agent communication
- Configuration via Pydantic models

### Milestone 3.2 — ADK CLI
- `agentic init <name>` — scaffold new agent project
- `agentic run <file>` — run agent locally with dev server
- `agentic test <file>` — run agent tests in sandbox
- `agentic build <dir>` — package agent for distribution

### Milestone 3.3 — Example Agents
- `hello_agent` — minimal agent with one tool
- `file_reader` — read files with permission check
- `web_fetcher` — fetch URLs with rate limiting
- `multi_agent_chat` — two agents communicating via bus

**Timeline:** 3–4 weeks
**Dependencies:** Phase 2 (runtime)

---

## Phase 4: System Services

**Goal:** Core AI services — inference, context, tool execution, communication.

### Milestone 4.1 — Inference Engine
- ONNX Runtime integration
- Model loading/unloading endpoint
- Request batching across agents
- Token counting and budget enforcement
- Model cache with LRU eviction

### Milestone 4.2 — Context Management
- Per-agent persistent context store (JSON/protobuf)
- Context compression (summarization for long sessions)
- Cross-agent context sharing with ACL
- Vector store integration (planned: Chroma/Pinecone)

### Milestone 4.3 — Tool Execution Framework
- Secure subprocess runner with timeouts
- Built-in tool library (file ops, HTTP, calculator, search)
- Output size limits and validation
- Tool chaining (pipeline composition)

### Milestone 4.4 — Communication Bus
- In-process message queue (→ Redis for distributed)
- Pub/sub and request/reply patterns
- Message routing by agent ID or capability
- Rate limiting and backpressure

**Timeline:** 8–12 weeks
**Dependencies:** Phase 2

---

## Phase 5: Security & Isolation

**Goal:** Production-grade sandboxing and access control.

### Milestone 5.1 — Capability Model
- Capability tokens per agent (filesystem, network, inference, etc.)
- Request/approve/release capability flow
- Granular permissions (read-only vs. read-write)

### Milestone 5.2 — Sandboxed Execution
- Container-based isolation (Docker/Podman initially)
- Namespace isolation (pid, net, mount)
- Resource limits (CPU shares, memory max, disk quota)
- Seccomp/AppArmor profiles

### Milestone 5.3 — Audit & Observability
- Structured audit log (agent actions, resource changes)
- Decision trace visualization
- OpenTelemetry integration
- Prometheus metrics endpoint

**Timeline:** 6–8 weeks
**Dependencies:** Phase 3, Phase 4

---

## Phase 6: Production & Ecosystem

**Goal:** Scalable, reliable, multi-machine deployment.

### Milestone 6.1 — Distributed Agent Execution
- Agent migration across machines
- Load balancing by resource availability
- Federated learning support

### Milestone 6.2 — Orchestration Engine
- DAG-based workflow definitions (YAML/JSON)
- Parallel, sequential, conditional execution
- Retry, error handling, circuit breaker patterns
- Webhook triggers and scheduled workflows

### Milestone 6.3 — Agent Marketplace
- Agent package registry
- Version management and dependency resolution
- Community ratings and security scanning

**Timeline:** 12+ weeks
**Dependencies:** All previous phases

---

## Phase 7: Federation & Trust Network

**Goal:** Let independently-operated AgenticOS nodes discover each other over the open web and verify each other's agents' identity and capabilities without a shared operator. Blockchain use is scoped narrowly — identity, attestation, and audit anchoring only. Execution, scheduling, and messaging stay off-chain, consistent with the local-first design principle.

### Milestone 7.1 — Decentralized Identity & Capability Attestation
- Ed25519 keypair per node and per agent; DID (`did:key`) as portable identity
- Signed capability credentials — an agent's capability claim is a credential signed by its issuing node, verifiable by any other node offline
- Local revocation registry with a sync endpoint
- `verify_credential(credential)` — validate a capability claim without contacting the issuer

### Milestone 7.2 — Federated Discovery & Communication
- Node registry: publish/discover peer endpoints + public keys (bootstrap via a shared directory service first; DHT/libp2p-style discovery later)
- Signed, encrypted inter-node messages — extends the Communication Bus (Phase 4.4) from a local broker to a WAN transport
- Replay protection (nonce + timestamp) and per-peer rate limiting

### Milestone 7.3 — Immutable Audit Anchoring
- Periodic hashing of agent action/audit logs into a Merkle root per interval
- Anchor Merkle roots to a public chain or L2 (chain selection deferred; prototype on a testnet)
- `verify_anchor(entry, root)` — prove a historical log entry is included in an anchored root

### Milestone 7.4 — Trust-Minimized Marketplace (Exploratory)
- Escrow contract for cross-node task payment
- Staking/slashing tied to the reputation built from 7.1–7.3 attestation history
- Dispute resolution process
- Deferred until 7.1–7.3 are validated with real cross-node usage — payments are the highest-risk, highest-complexity piece and shouldn't be designed against hypothetical usage patterns

**Timeline:** 10–14 weeks for Milestones 7.1–7.3. Milestone 7.4 is exploratory — no estimate until scope is validated by real usage.
**Dependencies:** Phase 4 (Communication Bus), Phase 5 (Capability Model)

---

## Timeline Summary

```
Phase 0: Docs & Structure        ██░░░░░░░░░░░░░░░░░░  1 week
Phase 1: Backend + Integration   ██████░░░░░░░░░░░░░░  3 weeks
Phase 2: Agent Runtime           ████████████░░░░░░░░  6 weeks
Phase 3: ADK                     ████████████████░░░░  4 weeks
Phase 4: System Services         ████████████████████░  12 weeks
Phase 5: Security                █████████████████████  8 weeks
Phase 6: Production              █████████████████████  12+ weeks
Phase 7: Federation & Trust      █████████████░░░░░░░░  10-14+ weeks
```

**Total estimated time to MVP (Phases 0–2):** ~10 weeks  
**Total estimated time to production (Phases 0–5):** ~34 weeks  
**Total estimated time to a federated network (Phases 0–7):** ~44+ weeks, with Milestone 7.4 open-ended

---

## How to Contribute

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for detailed guidance on:
- Environment setup
- Coding standards
- PR workflow
- Where to start based on skill set