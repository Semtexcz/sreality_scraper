---
task: TASK-039
status: "done"
priority: P1
type: feature
---

# Propagate location intelligence into modeling inputs

Task: TASK-039
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-032, TASK-036, TASK-037, TASK-038

## Problem

Location-derived features only create value for price prediction when they cross
the enrichment boundary into the canonical modeling contract in a controlled way.
At the moment, the modeling stage exposes only a few simple location flags, which
is far too weak for the expected importance of geography in apartment pricing.

## Definition of Done

- [x] Extend `ModelingFeatureSet` with the approved location intelligence features
      from enrichment, including administrative identifiers, coordinates,
      macro-distance metrics, and nearby-place aggregates that are stable enough
      for direct model consumption.
- [x] Decide which fields remain categorical, which stay numeric, and which should
      be omitted from the canonical modeling contract despite being available in
      enrichment.
- [x] Keep the modeling boundary explicit about provenance so each model-facing
      location feature can be traced back to the enriched and normalized inputs.
- [x] Add focused regression coverage for the new location feature handoff from
      enrichment into modeling inputs.
- [x] Update any modeling version metadata and lineage expectations affected by the
      expanded location feature set.

## Notes

- Avoid flooding the modeling contract with every intermediate location helper
  field; include the compact set that is plausibly useful for training and scoring.
- Document whether coded identifiers are intended for direct model consumption or
  only for downstream preprocessing workflows.
- Reevaluate target leakage risk before promoting any lifecycle-like geographic
  proxy that may actually encode listing freshness rather than location quality.
