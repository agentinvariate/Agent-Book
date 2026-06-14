# Real Agents Catalog

This directory contains only real agents.

A real agent must:

```text
reason + decide + act
```

Supporting models such as books, buses, streams, flows, events, schemas, and operating patterns are not agents.

---

## Production Agents

```text
FabricOps Agent        = VPS, Kubernetes, Fabric, SurrealDB operator
Repair Agent           = safe repair planner and executor
Security Agent         = security observer, risk analyzer, escalation agent
Policy Agent           = OPA/OpenFGA/AuthZEN policy decision assistant
Audit Agent            = evidence, trace, and compliance record keeper
Cost Agent             = resource and cost optimization agent
Release Agent          = CI/CD, release, provenance, promotion agent
Documentation Agent    = docs, runbooks, incident writeups, changelog agent
Data Agent             = data movement, quality, lineage, and pipeline agent
```

---

## Agent Contract

Every real agent must include:

```text
agent.yaml
system.md
tools.yaml
policy.md
runbook.md
examples/
```

---

## Runtime Rule

```text
Observe → Retrieve → Reason → Plan → Authorize → Act → Verify → Record → Learn
```

No action can run before authorization.
