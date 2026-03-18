---
task: TASK-037
status: "backlog"
priority: P1
type: feature
---

# Add coordinate and macro-distance location enrichment

Task: TASK-037
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-035, TASK-036

## Problem

Even with stable municipality codes, the model will still miss the continuous
spatial structure that strongly affects housing prices. The bundled coordinate
dataset enables a pragmatic first spatial layer, but the current enriched
contract exposes no latitude, longitude, or distance-based geographic features.

## Definition of Done

- [ ] Extend enrichment with reference-backed coordinate features, including at
      least `municipality_latitude` and `municipality_longitude`.
- [ ] Add deterministic macro-distance features such as
      `distance_to_okresni_mesto_km` and `distance_to_orp_center_km`.
- [ ] Decide and implement the canonical source point used for each distance
      computation, including how municipality centroids and ORP or district-city
      reference points are resolved.
- [ ] Keep coordinate and distance features optional when no trustworthy reference
      mapping exists.
- [ ] Add focused tests that validate distances for ordinary municipalities,
      district cities, and unresolved reference matches.

## Notes

- Great-circle or other distance calculations must be deterministic and documented.
- Municipality centroids are an acceptable first approximation outside large urban
  areas, but the implementation should not claim parcel-level precision.
- These features should be numerical and model-friendly, not just metadata for
  operator display.
