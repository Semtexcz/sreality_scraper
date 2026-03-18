---
task: TASK-033
status: "backlog"
priority: P2
type: feature
---

# Add listing freshness and lifecycle enrichment features

Task: TASK-033
Status: backlog
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-019, TASK-021

## Problem

Normalized records expose reliable `listed_on` and `updated_on` dates, but
enrichment does not yet derive any lifecycle semantics from them. That leaves
useful temporal signals such as listing freshness or days on market unavailable at
the canonical enriched boundary.

## Definition of Done

- [ ] Extend enrichment with deterministic lifecycle-derived features computed from
      normalized listing dates only.
- [ ] Add explicit numeric features for listing age and update recency using a
      documented deterministic reference timestamp.
- [ ] Add optional bucketed freshness flags only when their threshold rules are
      clearly documented and tested.
- [ ] Keep lifecycle features optional when date inputs are missing or logically
      inconsistent.
- [ ] Add regression coverage that proves enrichment stays deterministic for the
      same normalized snapshot.

## Notes

- Use the normalized or enriched timestamp as the deterministic reference point
  instead of the system clock at runtime.
- Decide how to handle negative durations when source dates are inconsistent, and
  document that behavior explicitly.
- This task should not introduce business assumptions about sale completion or
  delisting because the source dataset does not provide those facts directly.
