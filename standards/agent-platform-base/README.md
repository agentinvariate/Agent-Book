# Agent Platform Base Standard

## Production Base for Agent Book, Runtime, Data, Events, Governance, and Operations

**Author:** Chinmay Panda  
**Platform:** AGenNext / Fabric  
**Edition:** 1.0  
**Published:** 2026-06-14

---

## 1. Purpose

This standard fills the production gaps in the Agent Book repository.

It separates real agents from supporting models and infrastructure.

A real agent must reason, decide, and act.

Everything else is a model, contract, protocol, stream, bus, flow, workflow, or operating pattern.

---

## 2. Canonical Taxonomy

```text
Real Agents
├── FabricOps Agent
├── Repair Agent
├── Security Agent
├── Policy Agent
├── Audit Agent
├── Cost Agent
├── Release Agent
├── Documentation Agent
└── Data Agent

Supporting Standards
├── Agent Book
├── Agent Data Model
├── Agent Runtime Contract
├── Agent Memory Model
├── Agent Tool Contract
├── Agent Governance Contract
├── Agent Event Contract
├── Agent Evidence Model
├── Agent Trust Model
├── Agent Chat UI Contract
├── Agent Data Flow
├── Agent Event Bus
├── Agent Event Stream
├── Agent Storm Model
├── Agent Cyclone Pattern
└── Syborg Operating Model
```

Rule:

```text
If it cannot reason + decide + act, do not call it an agent.
```

---

## 3. Repository Base Layout

```text
standards/
  agent-platform-base/
  agent-platform-taxonomy/

schemas/
  agent.schema.json
  agent-book.schema.json
  tool.schema.json
  memory.schema.json
  policy.schema.json
  event.schema.json
  evidence.schema.json
  trust.schema.json
  run.schema.json

contracts/
  runtime.md
  chat-ui.md
  governance.md
  connectors.md
  events.md

surrealdb/
  schema.surql
  seed.surql

policies/
  opa/
    agent.rego
    destructive-actions.rego
    tool-risk.rego

runbooks/
  install.md
  verify.md
  uninstall.md
  troubleshoot.md

.github/workflows/
  validate.yml
```

---

## 4. Minimum Production Base

A production-ready agent platform must include:

```text
1. Canonical taxonomy
2. JSON Schemas
3. JSON-LD shape
4. CloudEvents event contract
5. SurrealDB schema
6. Runtime contract
7. Governance contract
8. OPA policy examples
9. Chat UI contract
10. Connector strategy
11. CI validation
12. Install / verify / uninstall runbooks
13. Security base
14. Release base
```

---

## 5. Runtime Loop

```text
Observe
  ↓
Retrieve
  ↓
Reason
  ↓
Plan
  ↓
Authorize
  ↓
Act
  ↓
Verify
  ↓
Record
  ↓
Learn
```

Invariant:

```text
Authorize always precedes Act.
```

---

## 6. Governance Base

Default rule:

```text
Deny by default.
```

Every action must pass:

```text
Identity check
Permission check
Policy check
Risk check
Approval check when required
Audit recording
```

Irreversible actions require explicit human approval.

---

## 7. Connector Roles

```text
Apache SeaTunnel = data movement engine
Apache Airflow   = scheduled workflow orchestration
Apache EventMesh = event routing backbone
CloudEvents      = canonical event envelope
SurrealDB/Fabric = memory, graph, state, evidence, audit
DeepAgents       = reasoning runtime harness
LangGraph        = stateful execution graph
OPA              = policy decision
OpenFGA          = relationship authorization
```

---

## 8. Release Gate

A release is valid only when:

```text
schemas validate
markdown links pass
shell scripts lint
OPA policies test
SurrealDB schema parses
runtime contract exists
security guardrails exist
runbooks exist
changelog updated
```

---

## 9. Final Standard

The platform must be:

```text
Readable
Schema-bound
Event-driven
Policy-governed
Evidence-producing
Human-approvable
Runtime-executable
Auditable
Recoverable
Versioned
```
