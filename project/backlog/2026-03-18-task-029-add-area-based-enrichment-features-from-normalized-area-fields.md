---
task: TASK-029
status: "backlog"
priority: P1
type: feature
---

# Add area-based enrichment features from normalized area fields

Task: TASK-029
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-019, TASK-023

## Problem

The enrichment stage still derives `floor_area_sqm` from title text even though
normalization now exposes explicit typed area fields under `area_details`. That
keeps one of the core derived metrics dependent on regex parsing and prevents the
stage from using the richer distinction between usable area and total area already
present in normalized artifacts.

## Definition of Done

- [ ] Extend the enrichment contract with typed area-based derived features sourced
      from `normalized_record.area_details` only.
- [ ] Define an explicit precedence rule for the canonical area value used in
      downstream price-density calculations.
- [ ] Add at least `price_per_usable_sqm_czk`, `price_per_total_sqm_czk`, and one
      clearly named canonical area feature for downstream consumers.
- [ ] Keep all new features optional when source normalized area fields are missing
      or zero.
- [ ] Update enrichment tests so area-derived behavior is validated from normalized
      fixtures without title parsing.

## Notes

- Favor `usable_area_sqm` over `total_area_sqm` when one canonical living-area
  feature is needed, but document the precedence explicitly in derivation notes.
- This task should remove title-regex dependence for floor-area derivation.
- Update enrichment and modeling contract versions if the canonical feature set
  changes.
