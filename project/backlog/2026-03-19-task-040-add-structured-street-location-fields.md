---
task: TASK-040
status: "todo"
priority: P1
type: feature
---

# Add structured street location fields

Task: TASK-040
Status: todo
Priority: P1
Type: feature
Author:
Created: 2026-03-19
Related: TASK-020, TASK-035, TASK-036

## Problem

The current normalization and enrichment contracts keep municipality and district
location data, but they do not preserve street names as first-class structured
fields. Street-like fragments can still appear inside raw titles, yet they are
discarded before the canonical normalized and enriched outputs are written. That
gap weakens downstream geospatial analysis, reduces traceability for precise
urban location signals, and makes later address-aware feature engineering harder
than it needs to be.

## Definition of Done

- [ ] Extend the normalized location contract with an explicit structured street
      field and source provenance that distinguish street text from municipality
      and district values.
- [ ] Implement conservative extraction rules so street values are captured only
      when the source title or payload provides a sufficiently reliable signal,
      and ambiguous fragments remain unset rather than guessed.
- [ ] Propagate the approved street representation into the enriched contract if
      that boundary is the right canonical place for downstream consumers to read
      it.
- [ ] Add regression coverage for Prague and non-Prague listings whose titles
      combine disposition, area, street, and municipality text without stable
      separators.
- [ ] Update enrichment or normalization version metadata and artifact
      expectations if the canonical contracts change.

## Notes

- Keep street extraction conservative; a missing street is preferable to an
  incorrect one.
- Preserve a clear distinction between street, municipality, city district, and
  broader location descriptors such as `Centrum obce`.
- Reuse existing source-backed title parsing rules where possible instead of
  introducing broad heuristics that silently reshape unrelated title fragments.
