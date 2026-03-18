---
task: TASK-036
status: "backlog"
priority: P1
type: feature
---

# Add reference-backed municipality and administrative location features

Task: TASK-036
Status: backlog
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-035

## Problem

The normalized location contract currently preserves only free-text municipality
and district labels. That is not strong enough for stable downstream analytics,
because names can collide across districts and because external reference data in
the repository already provides municipality, district, and region identifiers
that could anchor price modeling on much more reliable geography.

## Definition of Done

- [ ] Join normalized municipality labels against `data/souradnice.csv` using a
      documented deterministic matching strategy.
- [ ] Extend the canonical pipeline output with stable administrative identifiers,
      including at least `municipality_code`, `district_code`, `region_code`, and
      the matched municipality name from the reference dataset.
- [ ] Derive reference-backed boolean or categorical features such as
      `is_district_city` and `is_orp_center` using
      `data/OkresniMesta.csv` and `data/ObceSRozsirenouPusobnosti.csv`.
- [ ] Add a normalized or enriched representation of `city_district_normalized`
      when the source district label can be stabilized without inventing data.
- [ ] Add regression coverage for duplicate municipality names, Prague listings,
      and non-matching locations that must remain explicitly unresolved.

## Notes

- Matching should remain conservative: unresolved or ambiguous joins are better
  than silent incorrect municipality assignments.
- Municipality reference matching may need district-aware disambiguation when the
  same municipality name appears multiple times in the source table.
- Preserve both the source-facing label and the matched reference identity.
