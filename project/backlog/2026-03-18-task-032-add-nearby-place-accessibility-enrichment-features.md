---
task: TASK-032
status: "backlog"
priority: P1
type: feature
---

# Add nearby-place accessibility enrichment features

Task: TASK-032
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-024, TASK-025, TASK-028

## Problem

The normalized dataset already includes structured nearby-place facts for most
listings, but enrichment currently ignores that location context entirely. This
means the richest location signal in the dataset is unavailable to downstream
consumers unless they manually traverse and aggregate `location.nearby_places`.

## Definition of Done

- [ ] Extend enrichment with deterministic accessibility features computed from
      `location.nearby_places` only.
- [ ] Add nearest-distance features for at least public transport and essential
      daily services, using documented category groupings.
- [ ] Add one or more compact amenity-density features such as counts of nearby
      places within fixed distance thresholds.
- [ ] Define how duplicate or overlapping transport categories contribute to the
      derived features so results remain stable.
- [ ] Add focused tests for Prague and non-Prague fixtures, including records with
      partial nearby-place parsing and missing distances.

## Notes

- Favor a small, explainable feature set over many category-specific columns.
- Public transport can be modeled as grouped minima from categories such as
  `metro`, `tram`, `bus_mhd`, and `vlak`, but the grouping rules must be explicit.
- Missing `distance_m` values should not cause the whole feature family to fail.
