---
task: TASK-041
status: "todo"
priority: P1
type: design
---

# Design a multi-level geocoding contract

Task: TASK-041
Status: todo
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-040

## Problem

The current location intelligence layer stores municipality-centroid coordinates
only, which is too coarse for price-surface analysis and too ambiguous for
street-level listings. Before implementing richer geospatial logic, the project
needs an explicit contract for address-derived coordinates, fallback coordinates,
precision, confidence, and provenance so downstream enrichment and modeling stay
deterministic.

## Definition of Done

- [ ] Define the canonical normalized and/or enriched geocoding fields needed for
      multiple spatial precision levels, including exact-address, street,
      district, and municipality fallbacks where applicable.
- [ ] Specify explicit fields for `location_precision`, `geocoding_source`,
      `geocoding_confidence`, and any text inputs preserved for traceability.
- [ ] Decide which geocoding attributes belong in normalization, which belong in
      enrichment, and which should remain modeling-only derived helpers.
- [ ] Document acceptable fallback behavior when only partial address data is
      available and when geocoding remains unresolved.
- [ ] Define artifact and versioning implications for the approved contract.

## Notes

- The contract must let later stages distinguish precise coordinates from coarse
  municipality centroids without inferring that distinction indirectly.
- Confidence should stay explicit and machine-readable rather than embedded in
  free-text notes.
- Preserve enough source text to support later geocoder swaps or replay runs.
