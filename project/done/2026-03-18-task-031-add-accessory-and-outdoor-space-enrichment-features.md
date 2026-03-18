---
task: TASK-031
status: "done"
priority: P2
type: feature
---

# Add accessory and outdoor space enrichment features

Task: TASK-031
Status: done
Priority: P2
Type: feature
Author:
Created: 2026-03-18
Related: TASK-026, TASK-027, TASK-028

## Problem

Normalization now preserves elevator presence, barrier-free access, furnishing
state, and measured accessory areas, but enrichment does not yet transform those
facts into the compact derived features that downstream datasets typically expect.
This is one of the clearest gaps between the normalized schema and the current
enriched contract.

## Definition of Done

- [x] Extend enrichment with derived accessory features sourced only from
      `core_attributes.accessories`.
- [x] Add explicit booleans for key accessory presence, including balcony, loggia,
      terrace, cellar, elevator, and barrier-free access when those values are
      known.
- [x] Add one deterministic outdoor-area aggregate derived from balcony, loggia,
      and terrace measurements.
- [x] Preserve furnishing state as a stable derived categorical feature if it does
      not simply duplicate the normalized representation without added value.
- [x] Add tests covering listings with measured accessories, absent accessories,
      and ambiguous accessory source fragments.

## Notes

- Treat normalized accessory fields as the canonical source; do not inspect raw
  `source_specific_attributes` in enrichment.
- Parking should remain conservative because the normalized dataset still contains
  ambiguous garage-style fragments.
- Keep feature names explicit about whether they represent presence, area, or a
  combined aggregate.
