---
task: TASK-042
status: "done"
priority: P1
type: feature
---

# Add multi-level geocoding and location precision

Task: TASK-042
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-040, TASK-041

## Problem

Even after structured street extraction lands, downstream consumers still need a
usable coordinate strategy when address detail is incomplete. A deterministic
multi-level geocoding implementation is required so listings can resolve to the
best available point while preserving whether that point represents an exact
address, a street-level approximation, a district-level fallback, or only the
municipality centroid.

## Definition of Done

- [x] Implement the approved multi-level geocoding contract using the best
      available structured location inputs while preserving deterministic replay
      behavior.
- [x] Populate explicit precision and confidence fields so consumers can filter
      or weight listings by spatial reliability.
- [x] Preserve geocoding provenance, including the geocoded input text and the
      mechanism or dataset used to resolve the coordinate.
- [x] Add regression coverage for exact-address, street-only, district-only, and
      municipality-only fallbacks plus unresolved cases.
- [x] Update version metadata and persisted artifact expectations for any
      canonical contract changes introduced by geocoding.

## Notes

- Coarse municipality coordinates should remain available as a fallback, but
  they must no longer masquerade as listing-level precision.
- Deterministic replay matters more than maximizing recall with unstable
  third-party geocoders.
- The resulting data should support later uncertainty-aware map rendering.
