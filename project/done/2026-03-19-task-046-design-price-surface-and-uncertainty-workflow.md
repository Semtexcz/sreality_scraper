---
task: TASK-046
status: "done"
priority: P2
type: design
---

# Design a price-surface and uncertainty workflow

Task: TASK-046
Status: done
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

- [x] Define the first supported workflow for generating a map-ready apartment
      price surface from listing-level observations.
- [x] Compare grid aggregation, kernel smoothing, and spatial-regression-style
      approaches in terms of replayability, interpretability, and data
      requirements for this repository.
- [x] Specify how coordinate precision and geocoding confidence affect map
      inclusion, weighting, or uncertainty.
- [x] Define at least one uncertainty output so coarse geocodes and sparse areas
      are visible instead of being rendered with false precision.
- [x] Document the artifacts, contracts, and staged dependencies needed before
      implementation begins.

## Notes

- A scalar price map should not imply equal confidence across all locations.
- Separate the design of the price surface from any eventual UI or API delivery
  mechanism.
- Favor a first workflow that can be reproduced fully from persisted artifacts.

## Design Decision

`TASK-046` approves a deterministic grid-aggregation workflow as the first
supported repository path for map-ready scalar price outputs.

The canonical first implementation must:

1. consume the later approved analysis dataset rather than raw or normalized
   artifacts directly
2. use `price_per_square_meter_czk` as the scalar target
3. aggregate listings into one approved spatial grid resolution
4. use the median per cell as the primary scalar value
5. expose explicit uncertainty sidecars such as listing count, interquartile
   spread, and coverage status
6. exclude district-level, municipality-level, or unresolved coordinates from
   the canonical cell-level map instead of smoothing them into false precision

Kernel smoothing and spatial-regression-style approaches remain optional future
comparators, but they are not approved as the first supported workflow because
they are harder to audit, easier to overstate visually, and more dependent on
later modeling decisions.

## Contract And Artifact Outcome

The approved repository-level design is documented in
`docs/PRICE_SURFACE_WORKFLOW.md`.

That design defines:

- the candidate-method comparison
- the precision-aware inclusion and weighting policy
- the required uncertainty outputs
- the cell-level derived artifact contract
- the staged dependencies for `TASK-053` through `TASK-056`
