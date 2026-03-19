---
task: TASK-044
status: "todo"
priority: P1
type: feature
---

# Add multi-center and accessibility location features

Task: TASK-044
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-042, TASK-043

## Problem

Apartment prices are not driven only by municipality identity. They respond to
accessibility and to multiple urban centers such as historic cores, employment
hubs, and main public transport nodes. The current location layer lacks this
continuous spatial structure, which makes it too weak for scalar price-map
estimation.

## Definition of Done

- [ ] Define and implement deterministic distance-based features to relevant city
      centers rather than relying on a single municipality center only.
- [ ] Add accessibility features for key mobility anchors such as metro, tram,
      rail, and other backbone public transport where the reference data supports
      stable derivation.
- [ ] Decide which center definitions are canonical for Prague and other major
      Czech cities and how smaller municipalities should degrade gracefully.
- [ ] Add regression coverage for multi-center urban listings and for smaller
      municipalities with limited center metadata.
- [ ] Update version metadata and documentation for the approved accessibility
      feature set.

## Notes

- Multiple center distances should be explicit features, not hidden inside one
  composite score.
- Use deterministic reference points or datasets only; avoid live routing APIs in
  the canonical enrichment pipeline unless a replay-safe strategy exists.
- This task should improve the continuous spatial signal without assuming prices
  respect official boundaries.
