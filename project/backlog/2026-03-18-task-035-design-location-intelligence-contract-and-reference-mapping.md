---
task: TASK-035
status: "backlog"
priority: P1
type: design
---

# Design location intelligence contract and reference mapping

Task: TASK-035
Status: backlog
Priority: P1
Type: design
Author:
Created: 2026-03-18
Related: TASK-019, TASK-029, TASK-032

## Problem

Location is expected to be the strongest driver of apartment asking prices, but
the current pipeline stops at `city`, `city_district`, and `nearby_places`
without a deliberate contract for administrative mapping, reference-data joins,
coordinate provenance, or spatial feature semantics. Without that design, later
implementation work will drift into ad hoc heuristics and unstable model inputs.

## Definition of Done

- [ ] Define where reference-backed location intelligence belongs across
      normalization, enrichment, and modeling boundaries.
- [ ] Decide the canonical fields for municipality identity, administrative codes,
      coordinates, district-center membership, and spatial buckets.
- [ ] Document the provenance and fallback rules for joining normalized locations
      to bundled reference datasets such as `data/souradnice.csv`,
      `data/OkresniMesta.csv`, and `data/ObceSRozsirenouPusobnosti.csv`.
- [ ] Define how ambiguous municipality names, Prague-style numbered districts,
      and missing district labels should be represented without hiding uncertainty.
- [ ] Identify any contract version bumps required by the proposed location
      intelligence fields.

## Notes

- Keep direct source reshaping in normalization and derived interpretation in
  enrichment; do not collapse both concerns into one stage.
- The design should make room for both human-readable names and stable coded
  identifiers.
- Prefer explicit provenance fields over silent best-effort matching.
