---
task: TASK-038
status: "done"
priority: P2
type: feature
---

# Add metropolitan district and spatial cell location features

Task: TASK-038
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-035, TASK-036, TASK-037

## Problem

Municipality-level coordinates are often too coarse inside Prague and other large
cities where micro-location drives price differences strongly. The pipeline needs
a more expressive but still deterministic representation for large urban areas so
the model is not forced to learn those differences from city labels alone.

## Definition of Done

- [x] Add a documented metropolitan-location layer for large cities, starting with
      Prague and leaving room for Brno and Ostrava if the normalized data justifies
      it.
- [x] Define and implement stable derived features such as
      `metropolitan_area`, `metropolitan_district`, and a spatial bucket field such
      as `spatial_cell_id`.
- [x] Add one or more city-center distance features for supported metropolitan
      areas, for example `distance_to_prague_center_km`, when the reference point
      is clearly documented.
- [x] Keep all metropolitan features optional outside supported cities or when the
      source district data is too ambiguous.
- [x] Add tests covering Prague numbered-district inputs, named city districts,
      and non-metropolitan municipalities.

## Notes

- Prefer stable spatial cells or grids over brittle free-text micro-location
  heuristics.
- The first version does not need parcel-level geocoding; municipality-level
  coordinates plus district-aware bucketing is sufficient.
- Do not overgeneralize Prague-specific logic to the whole country without an
  explicit rule set.
