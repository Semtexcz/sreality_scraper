---
task: TASK-023
status: "done"
priority: P2
type: feature
---

# Add derived price, building, and energy enrichment

Task: TASK-023
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-014, TASK-019, TASK-022

## Problem

Once normalization exposes direct typed source facts for price, floor position,
building state, and energy efficiency, the enrichment stage should derive the
higher-level semantics that are useful for downstream analysis. Those values do not
belong in normalization because they require interpretation across multiple
normalized fields rather than direct reshaping of one raw payload string.

## Definition of Done

- [x] Extend enrichment to compute derived price, building, or energy features only
      from normalized records.
- [x] Consider features such as `price_per_sqm`, `is_top_floor`, `is_new_build`,
      and energy buckets only when they can be defined explicitly and tested
      deterministically.
- [x] Keep every derived feature optional when source normalized fields are missing
      or ambiguous.
- [x] Preserve traceability back to the full normalized input record so operators can
      understand how each derived feature was produced.
- [x] Add focused tests that verify derivation behavior from normalized fixtures
      rather than raw source payloads.

## Notes

- This task depends on richer normalized source-backed fields from TASK-022.
- Do not re-parse raw payload text in enrichment.
- Favor a small set of clearly defined derived features over a broad heuristic layer.
