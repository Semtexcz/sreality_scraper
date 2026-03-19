---
task: TASK-045
status: "todo"
priority: P2
type: feature
---

# Add neighborhood intensity and environment location features

Task: TASK-045
Status: todo
Priority: P2
Type: feature
Author:
Created: 2026-03-19
Related: TASK-042, TASK-043, TASK-044

## Problem

Price differences between nearby apartments often come from neighborhood quality
signals rather than from administrative identity alone. The current pipeline has
only limited nearby-place data and does not yet capture broader local amenity
density, environmental quality, or urban-form context that could explain the
micro-location component of a price surface.

## Definition of Done

- [ ] Define the approved neighborhood and environmental feature subset that is
      stable enough for canonical enrichment or modeling inputs.
- [ ] Add deterministic local-intensity features such as amenity density or
      service counts across documented radii where the underlying reference data
      supports reliable replay.
- [ ] Evaluate additional environment signals such as proximity to parks, water,
      major roads, or other locally important urban context if those inputs can be
      sourced deterministically.
- [ ] Add regression coverage that demonstrates the features distinguish nearby
      micro-locations without leaking target information.
- [ ] Update version metadata and documentation for the expanded local context
      feature set.

## Notes

- Keep this task focused on durable exogenous location features, not on rolling
  market statistics derived from the target variable itself.
- Use a conservative inclusion bar: a smaller reliable subset is better than a
  wide but weakly sourced bundle of proxies.
- Neighborhood intensity should complement, not replace, the coordinate, grid,
  and center-distance layers.
