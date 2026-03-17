---
task: TASK-014
status: "done"
priority: P2
type: feature
---

# Add the enrichment stage on top of normalized data

Task: TASK-014
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-17
Related: TASK-010, TASK-011, TASK-013, TASK-015

## Problem

Derived features should exist, but they should not leak into scraping or
normalization. Without a dedicated enrichment stage, future feature computation will
either pollute earlier modules or produce inconsistent inputs for modeling work.

## Definition of Done

- [x] Define the enriched record model that wraps or extends normalized data with derived features.
- [x] Implement the contract as a typed Python model.
- [x] Place the contract/component in the appropriate module boundary.
- [x] Implement an enrichment component that accepts normalized records only.
- [x] Keep the initial feature set explicit, deterministic, and documented.
- [x] Include an `enrichment_version` field in the enriched contract.
- [x] Preserve access to the underlying normalized values for debugging and traceability.
- [x] Add focused tests proving enrichment is isolated from scraping and normalization behavior.

## Notes

- Avoid network-dependent enrichment in V1 unless explicitly required.
- Favor a small starter feature set over a broad speculative schema.
- The output of this stage is the only valid input for modeling.
