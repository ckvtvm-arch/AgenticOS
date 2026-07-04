# AgenticOS Architecture

> **Version:** 1.2  
> **Last updated:** July 2026  
> **Status:** Planning / Early Development

---

## Overview

AgenticOS is designed as a layered system where AI agents are first-class execution units. The architecture follows a microkernel-inspired design with three primary layers: **Kernel**, **System Services**, and **User Space**.

```
┌─────────────────────────────────────────────────────┐
│                    User Space                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  ADK     │  │  System  │  │  Orchestration    │  │
│  │  (SDK)   │  │  Agent   │  │  Framework        │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────┤
│                  System Services                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ ┌─────────┐    │
│  │Agent │ │Infer-│ │Con-  │ │Tool│ │Communi- │    │
│  │Regis-│ │ence  │ │text  │ │Exe-│ │cation   │    │
│  │try   │ │Engine│ │Mgt   │ │cute│ │Bus      │    │
│  └──────┘ └──────┘ └──────┘ └────┘ └─────────┘    │
├─────────────────────────────────────────────────────┤
│                     Kernel                           │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐│
│  │  Agent   │  │    Memory    │  │   Isolation   ││
│  │Scheduler │  │   Manager    │  │    Engine     ││
│  └──────────┘  └──────────────┘  └────────────────┘│
├─────────────────────────────────────────────────────┤
│               Hardware Abstraction Layer             │
│  CPU  │  GPU/TPU  │  RAM  │  Storage  │  Network    │
└─────────────────────────────────────────────────────┘
```
*(Goal Manager and Policy Decision Point — added in Phase 4 — are omitted above for space; see System Services Layer below.)*

---

## Layer Descriptions

### 1. Kernel Layer

The kernel is the core of AgenticOS, responsible for low-level resource management and agent lifecycle.

#### Agent Scheduler
- **Responsibility:** Allocate CPU/GPU time to agents based on priority and fairness policies.
- **Key operations:** spawn, pause, resume, terminate, hibernate agents.
- **Policies:** priority-based, round-robin, cooperative preemption (avoids interrupting mid-reasoning).
- **QoS:** Service-level objectives for latency-sensitive agents.

#### Memory Manager
- **Responsibility:** Manage unified memory for model weights, activations, and agent contexts.
- **Key features:**
  - Intelligent caching of frequently-used models.
  - Memory compression for large language models.
  - Shared memory pools for multi-agent collaboration.
  - Hot-swap of model weights between GPU and system RAM.

#### Agent Isolation Engine
- **Responsibility:** Sandbox agents to prevent interference and contain failures.
- **Mechanisms:**
  - Namespace isolation (filesystem, network, process).
  - Capability-based security tokens, enforced via the Policy Decision Point (System Services) rather than left to each agent's own code.
  - Resource quotas (CPU %, memory limit, GPU fraction).
  - Audit logging of all agent syscalls.

---

### 2. System Services Layer

A set of long-running daemons that provide foundational capabilities to all agents.

#### Agent Registry & Discovery
- **Responsibility:** Track all running and available agents.
- **API:**
  - `register(agent_info)` — agent announces itself.
  - `discover(capability)` — find agents with a given capability.
  - `heartbeat(agent_id)` — health check ping.
  - `deregister(agent_id)` — agent shutdown.
- **Storage:** In-memory with SQLite persistence for recovery.

#### Goal Manager (Phase 4)
- **Responsibility:** Track what agents are actually trying to accomplish, not just whether they're alive.
- **API:**
  - `submit_goal(description, agent_id)` — create a `Goal`/`Task`, optionally decomposed into subtasks.
  - `get_goal(goal_id)` — status (`pending`/`in_progress`/`succeeded`/`failed`) and result.
  - `cancel_goal(goal_id)` — propagate cancellation to in-flight subtasks.
- **Storage:** SQLite, alongside the agent registry.
- This is the prerequisite the Agent Orchestration Framework (User Space) sequences work against — without it there is nothing for an orchestrator to orchestrate.

#### Policy Decision Point (Phase 4)
- **Responsibility:** Decide whether an agent is allowed to take a given action, before it happens — not describe what it claims to be capable of after the fact.
- **API:** `check(agent_id, action) -> allow/deny`, called from the Tool Execution Framework and from Goal Manager assignment.
- **Policy:** deny-by-default; capabilities must be explicitly granted at registration. Every decision is written to the audit log.
- Phase 6's Capability Model extends this same decision engine down to the process/container boundary — the enforcement point gets stronger over time, but the decision logic doesn't fork into two separate systems.

#### Inference Engine Service
- **Responsibility:** Serve ML model inference to agents.
- **Capabilities:**
  - Model loading, caching, and hot-swapping.
  - Request batching across multiple agents.
  - Multi-backend: ONNX Runtime, TensorRT, OpenVINO.
  - Quantization and pruning support.
  - Token counting and budget enforcement.

#### Context Management Service
- **Responsibility:** Persist and share agent conversational/session state.
- **Capabilities:**
  - Per-agent context storage (JSON / protobuf serialization).
  - Context compression and summarization.
  - Cross-agent context sharing (ACL-protected).
  - Long-term memory (vector store integration planned).

#### Tool Execution Framework
- **Responsibility:** Run agent-requested tools in a secure sandbox.
- **Built-in tools:** File I/O, HTTP client, shell commands (whitelisted), calculator, data transform.
- **Features:**
  - Timeout enforcement.
  - Output size limits.
  - Result validation and sanitization.
  - Tool chaining/composition.

#### Communication Bus
- **Responsibility:** Enable inter-agent messaging.
- **Patterns:** pub/sub, request/reply, streaming.
- **Serialization:** Protocol Buffers or MessagePack.
- **Features:**
  - Message routing by agent ID or capability.
  - Rate limiting and backpressure.
  - Persistent message queues for offline agents.

---

### 3. User Space

Tools and interfaces for developers and end users.

#### Agent Development Kit (ADK)
- **Language:** Python (primary), TypeScript (secondary).
- **Components:**
  - `Agent` base class with lifecycle hooks: `on_start`, `on_pause`, `on_resume`, `on_terminate`.
  - `@tool` decorator to register functions as agent-callable tools.
  - `@on_message` handler for inter-agent messages.
  - Local dev server with hot reload.
- **CLI:** `agentic init`, `agentic run`, `agentic test`, `agentic build`.

#### System Agent
- A built-in default agent for system management tasks.
- Capabilities: system monitoring, proactive optimization, user preference learning.
- Natural language interface to OS functions.

#### Agent Orchestration Framework
- Sequences work against the Goal Manager's `Goal`/`Task` graph (Phase 4) — it does not maintain its own separate notion of what agents are doing.
- Define multi-agent workflows as DAGs.
- Coordination patterns: sequential, parallel, map/reduce, hierarchical.
- Error handling: retry, fallback, circuit breaker.
- Workflow templates for common patterns.

---

### 4. Federation Layer (Phase 8)

Everything above describes a single AgenticOS node. The Federation Layer is what lets independently-operated nodes discover each other over the open web and verify each other's claims without a shared operator — it sits beside the node stack, not inside it.

```
┌───────────────────────┐             ┌───────────────────────┐
│     AgenticOS Node A   │             │     AgenticOS Node B   │
│ (Kernel/Services/User  │             │ (Kernel/Services/User  │
│  Space, as above)      │             │  Space, as above)      │
└───────────┬───────────┘             └───────────┬───────────┘
            │                                     │
            ▼                                     ▼
┌───────────────────────────────────────────────────────────────┐
│                       Federation Layer                        │
│  ┌────────────┐  ┌───────────────────┐  ┌────────────────────┐│
│  │ Node ID &  │  │ Capability         │  │ Federated Message  ││
│  │ Discovery  │  │ Attestation &      │  │ Relay (signed,     ││
│  │ (DID)      │  │ Revocation Registry│  │ encrypted, WAN)    ││
│  └────────────┘  └───────────────────┘  └────────────────────┘│
└──────────────────────────────┬──────────────────────────────────┘
                                ▼
                  ┌───────────────────────────┐
                  │   Public Chain / L2        │
                  │   (identity anchors, audit │
                  │    log roots — not live    │
                  │    traffic or execution)   │
                  └───────────────────────────┘
```

#### Node Identity & Discovery
- **Responsibility:** Give every node and agent a portable, cryptographically verifiable identity that isn't scoped to one operator's database.
- **Mechanism:** Ed25519 keypair per node/agent; DID (`did:key`) as the identity format; a bootstrap directory service for peer discovery, with DHT/libp2p-style discovery as a later upgrade.

#### Capability Attestation & Revocation Registry
- **Responsibility:** Let one node trust another node's claim about what an agent can do, without contacting the issuer.
- **Mechanism:** Capability claims are signed credentials, verifiable offline; a revocation registry (synced between nodes) invalidates compromised or retired credentials.

#### Federated Message Relay
- **Responsibility:** Extend the in-process Communication Bus (System Services layer) across the WAN between mutually untrusted nodes.
- **Mechanism:** Signed and encrypted messages, nonce+timestamp replay protection, per-peer rate limiting.

#### Audit Anchor Service
- **Responsibility:** Make agent action/audit logs tamper-evident across the network without putting live traffic on-chain.
- **Mechanism:** Periodically hash audit logs into a Merkle root; anchor only the root to a public chain or L2; provide inclusion proofs for individual log entries.

**Deliberately out of scope for now:** on-chain payments/escrow. A trust-minimized marketplace (task payment, staking/slashing, dispute resolution) is a natural extension once attestation and audit anchoring are proven with real cross-node usage, but is not designed against hypothetical usage patterns — see Roadmap Milestone 8.4.

---

## Data Flow

```
  ┌──────────┐     ┌──────────────┐     ┌───────────┐
  │ Dashboard │────▶│  Backend API │────▶│  Agent    │
  │  (React)  │◀────│  (FastAPI)   │◀────│  Runtime  │
  └──────────┘     └──────┬───────┘     └───────────┘
                          │
                   ┌──────▼───────┐
                   │   Database   │
                   │   (SQLite)   │
                   └──────────────┘
```

1. **Dashboard** (React) polls or subscribes to the Backend API.
2. **Backend API** (FastAPI) forwards agent actions to the Agent Runtime.
3. **Agent Runtime** spawns/manages agent processes, collects metrics.
4. **Database** persists agent metadata, sessions, audit logs.
5. **System Services** (registry, inference, context) run as sidecar processes accessible via the Backend API.

---

## Current Implementation Status

| Layer | Component | Status | Notes |
|-------|-----------|--------|-------|
| UI | Dashboard | ✅ Done | React + Vite, simulated data |
| UI | AgentList | ✅ Done | Table with status + resource cols |
| UI | ResourceMonitor | ✅ Done | Animated progress bars |
| UI | SystemStatus | ✅ Done | Service health indicators |
| UI | ArchitectureView | ✅ Done | Static layer diagram |
| API | Backend Server | ✅ Done | FastAPI, `backend/app/main.py` |
| API | WebSocket | ✅ Done | Broadcasts on every registry change |
| Services | Agent Registry | ✅ Done | SQLite-persisted, survives restarts |
| Services | Goal Manager | ❌ Not Started | Phase 4.1 |
| Services | Policy Decision Point | ❌ Not Started | Phase 4.2 — no enforced permissions exist today |
| Services | Inference Engine | ❌ Not Started | |
| Services | Context Management | ❌ Not Started | |
| Services | Tool Execution | ❌ Not Started | |
| Services | Communication Bus | ❌ Not Started | |
| Kernel | Agent Scheduler | ⚠️ Partial | Basic priority queue + pause/resume; no cgroups, no fairness policy |
| Kernel | Memory Manager | ❌ Not Started | |
| Kernel | Isolation Engine | ❌ Not Started | Agents run as bare subprocesses today — no namespace/seccomp isolation |
| Dev | ADK (SDK) | ✅ Done | `backend/adk/sdk.py` |
| Dev | CLI | ✅ Done | `agentic init/run/test/build` |
| Dev | Orchestration Framework | ❌ Not Started | Phase 4.3 (foundations), Phase 7.2 (full engine) |
| Federation | Node ID & Discovery | ❌ Not Started | Phase 8.1/8.2 |
| Federation | Capability Attestation Registry | ❌ Not Started | Phase 8.1 |
| Federation | Federated Message Relay | ❌ Not Started | Phase 8.2 |
| Federation | Audit Anchor Service | ❌ Not Started | Phase 8.3 |

---

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Dashboard | React 19 + Vite + TypeScript | Fast dev cycle, rich ecosystem |
| Backend API | Python + FastAPI | Async, auto-docs, great DX |
| Database | SQLite (dev) → PostgreSQL (prod) | Zero-config for dev, scalable for prod |
| Real-time | WebSocket (via FastAPI) | Bidirectional, low-latency |
| Agent Runtime | Python subprocesses → containers | Iterate fast, then isolate |
| Serialization | Protocol Buffers | Compact, typed, cross-language |
| Model Serving | ONNX Runtime | Multi-framework support |
| Node/Agent Identity | DID (`did:key`) + Ed25519 | Portable identity, no chain dependency for basic verification |
| Audit Anchoring | Public L2 (chain TBD) | Low-cost, high-finality anchor point; avoid mainnet gas costs for periodic roots |
| Federated Transport | libp2p (candidate) | NAT traversal, pub/sub, built for WAN peer-to-peer |

---

## Design Principles

1. **Local-first:** Agents should work offline; cloud is optional.
2. **Fail-safe:** Agent crashes never take down the OS.
3. **Observable:** Every agent action is logged and measurable.
4. **Capability-based:** Agents get minimum permissions needed.
5. **Pluggable:** Each service can be swapped (inference backend, database, etc.).
6. **Trust-minimized federation:** Nodes verify other nodes' claims cryptographically rather than trusting a central operator.
7. **On-chain minimalism:** Only identity, capability attestation, and audit anchors touch a blockchain — execution, scheduling, and messaging stay off-chain.