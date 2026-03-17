---
task: TASK-013
status: "done"
priority: P1
type: feature
---

# Add the normalization stage and stable normalized contract

Task: TASK-013
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-17
Related: TASK-010, TASK-011, TASK-012, TASK-014, TASK-015

## Problem

Raw payloads mirror the source site and are therefore unstable as a direct input for
downstream consumers. The project needs a dedicated normalization stage that converts
raw scraper output into a stable internal structure while preserving traceability back
to the captured source record.

## Definition of Done

- [x] Define the canonical normalized record model produced from raw scraper output.
- [x] Implement the contract as a typed Python model.
- [x] Place the contract/component in the appropriate module boundary.
- [x] Implement a dedicated normalization component that converts raw records into the normalized contract.
- [x] Preserve source identity and provenance so normalized records can be traced back to the originating raw capture.
- [x] Include a `normalization_version` field in the normalized contract.
- [x] Document how missing, partial, or source-specific values are represented in the normalized structure.
- [x] Ensure normalization produces identical output for identical raw input.
- [x] Add deterministic tests for the normalized contract and representative mapping cases.

## Notes

- Normalization should standardize structure and field representation only.
- Do not compute derived analytics or modeling features in this stage.
- Keep the initial normalized contract as small as possible and expand it only when downstream needs are explicit.
