---
task: TASK-056
status: "backlog"
priority: P1
type: feature
---

# Implement grid-based price-surface and uncertainty analysis

Task: TASK-056
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-046, TASK-054, TASK-055

## Problem

The notebook is expected to produce a map-ready scalar price surface, but the
repository does not yet implement the first approved workflow for turning
listing-level observations into a defensible spatial value with visible
uncertainty. This gap blocks both article visuals and any later production
surface generation.

## Definition of Done

- [ ] Implement the first supported notebook workflow for aggregating listings
      into a grid-based scalar price surface.
- [ ] Use the approved target metric and aggregation method for the first map,
      including minimum local support thresholds.
- [ ] Surface at least one explicit uncertainty output so sparse or low-quality
      cells do not appear falsely precise.
- [ ] Ensure coordinate precision and approximation metadata influence map
      inclusion, weighting, or uncertainty labeling as approved by `TASK-046`.
- [ ] Document the resulting notebook outputs and any limitations needed for the
      blog article.

## Notes

- Favor median `price_per_square_meter_czk` and transparent support thresholds
  for the first implementation unless `TASK-046` approves something else.
- Keep continuous smoothing optional and clearly secondary to the first
  reproducible grid workflow.
- The notebook output should remain auditable back to the exported dataset.
