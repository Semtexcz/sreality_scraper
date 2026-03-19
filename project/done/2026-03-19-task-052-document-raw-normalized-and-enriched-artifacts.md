---
task: TASK-052
status: "done"
priority: P2
type: docs
---

# Document raw, normalized, and enriched artifacts

Task: TASK-052
Status: done
Priority: P2
Type: docs
Author:
Created: 2026-03-19
Related: TASK-012, TASK-013, TASK-014, TASK-021, TASK-034, TASK-050, TASK-051

## Problem

The repository documents stage boundaries and generated outputs at a high level,
but it does not yet provide a dedicated artifact reference that explains the
shape, ownership, lineage, and field-level semantics of the persisted `raw`,
`normalized`, and `enriched` JSON artifacts. As the contracts grow, operators
and future contributors need a predictable place to understand every important
field without reverse-engineering runtime models or sample payloads.

## Definition of Done

- [x] Add dedicated artifact-stage documentation for raw, normalized, and
      enriched outputs under `docs/`.
- [x] Document the storage layout and replay/lineage guarantees for each
      artifact family.
- [x] Include a field reference for each artifact that describes every
      top-level field and the important nested fields used as part of the
      canonical contract.
- [x] For each documented field, state its purpose, expected type or shape,
      whether it is required or optional, and which stage owns the value.
- [x] Make boundary rules explicit so readers can tell which fields are direct
      source facts, normalized source-backed values, or enrichment-owned
      derived features.
- [x] Include trimmed representative JSON examples that match the documented
      structure without turning the docs into raw payload dumps.
- [x] Update index-level documentation so readers can discover the new artifact
      references from the existing docs entrypoints.

## Notes

- Favor a data-dictionary style reference over narrative-only prose.
- Keep the structure parallel across raw, normalized, and enriched docs so
  readers can compare stages quickly.
- The documentation should explain both field semantics and stage ownership;
  field lists alone are not enough.
- Nested collections with open-ended source-specific keys can be documented as
  a bounded contract plus rules for how unknown keys are preserved.
