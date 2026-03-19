---
task: TASK-046
status: "todo"
priority: P2
type: design
---

# Design a price-surface and uncertainty workflow

Task: TASK-046
Status: todo
Priority: P2
Type: design
Author:
Created: 2026-03-19
Related: TASK-042, TASK-043, TASK-044, TASK-045

## Problem

The end goal is a scalar apartment price map rather than a table grouped by
administrative units. The project does not yet define how enriched and modeled
listing data should be transformed into a spatial price surface, how smoothing or
aggregation should work, or how uncertainty should be exposed when coordinate
precision is low or local sample density is sparse.

## Definition of Done

- [ ] Define the first supported workflow for generating a map-ready apartment
      price surface from listing-level observations.
- [ ] Compare grid aggregation, kernel smoothing, and spatial-regression-style
      approaches in terms of replayability, interpretability, and data
      requirements for this repository.
- [ ] Specify how coordinate precision and geocoding confidence affect map
      inclusion, weighting, or uncertainty.
- [ ] Define at least one uncertainty output so coarse geocodes and sparse areas
      are visible instead of being rendered with false precision.
- [ ] Document the artifacts, contracts, and staged dependencies needed before
      implementation begins.

## Notes

- A scalar price map should not imply equal confidence across all locations.
- Separate the design of the price surface from any eventual UI or API delivery
  mechanism.
- Favor a first workflow that can be reproduced fully from persisted artifacts.
