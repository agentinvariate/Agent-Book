# Artifact Pattern Registry

The registry contains reusable enterprise artifact patterns.

A pattern is not just a document template. It is a structured workflow that defines how Agent Book turns inputs, evidence, and governance rules into finished enterprise outputs.

## Pattern Files

Pattern definitions live in `registry/patterns/*.yaml`.

Each pattern should define:

- `id`
- `family`
- `name`
- `job_to_be_done`
- `required_inputs`
- `optional_inputs`
- `workflow`
- `sections`
- `outputs`
- `validators`
- `governance`

## Runtime Flow

```text
ArtifactPattern
  -> ArtifactRun
  -> WorkflowExecution
  -> GeneratedArtifact
  -> ValidationResult
  -> Export
```

## Current MVP Patterns

- `state_of_report`
- `product_comparison_article`
- `readiness_assessment`

## Design Principle

New artifact types should be added as registry definitions first. The core engine should remain generic and reusable.
