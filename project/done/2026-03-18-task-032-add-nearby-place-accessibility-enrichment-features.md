---
task: TASK-032
status: "done"
priority: P1
type: feature
---

# Add nearby-place accessibility enrichment features

Task: TASK-032
Status: done
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
- [ ] Add nearest-distance features for at least `nearest_public_transport_m`,
      `nearest_metro_m`, `nearest_tram_m`, `nearest_bus_m`, `nearest_train_m`,
      `nearest_shop_m`, `nearest_school_m`, and `nearest_kindergarten_m`, using
      documented category groupings.
- [ ] Add one or more compact amenity-density features such as counts of nearby
      places within fixed distance thresholds, including
      `amenities_within_300m_count` and `amenities_within_1000m_count` or an
      explicitly justified equivalent.
- [ ] Define how duplicate or overlapping transport categories contribute to the
      derived features so results remain stable.
- [ ] Add focused tests for Prague and non-Prague fixtures, including records with
      partial nearby-place parsing and missing distances.

## Notes

- Favor a small, explainable feature set over many category-specific columns.
- Public transport can be modeled as grouped minima from categories such as
  `metro`, `tram`, `bus_mhd`, and `vlak`, but the grouping rules must be explicit.
- Missing `distance_m` values should not cause the whole feature family to fail.
- Treat grouped transport and daily-service features as canonical model-facing
  location outputs, not just as internal helper aggregates.
