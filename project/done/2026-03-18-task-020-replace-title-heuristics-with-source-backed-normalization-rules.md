---
task: TASK-020
status: "done"
priority: P1
type: refactor
---

# Replace title heuristics with source-backed normalization rules

Task: TASK-020
Status: done
Priority: P1
Type: refactor
Author:
Created: 2026-03-18
Related: TASK-013, TASK-019, TASK-021

## Problem

The current normalizer still derives location fields by splitting the human-facing
`Název` string, even though the title is presentation-oriented and frequently
concatenates disposition, area, street, and municipality text without stable
separators such as `66m²Vítězná, Karlovy Vary - Drahovice`. The roadmap calls for
clearer field-level extraction rules where the source payload allows it. Without a
defined precedence policy, normalization remains coupled to brittle title formatting
and hides which fields are explicit source facts versus heuristic fallbacks.

## Definition of Done

- [x] Define and document extraction precedence for normalized fields so explicit
      detail-payload attributes are always preferred over title parsing.
- [x] Remove title-based parsing for any field that can be sourced from dedicated raw
      attributes introduced by the expanded normalization contract.
- [x] Rework location extraction so any remaining fallback parsing is isolated,
      explicitly documented, and covered by representative tests.
- [x] Ensure normalized outputs distinguish between directly mapped source facts and
      fallback heuristic values without leaking raw scraper models into downstream
      stages.
- [x] Add regression coverage for common title formats from `data/raw/all-czechia`,
      including Prague district patterns, non-Prague municipality listings, and
      titles with no clean separator between area and street text.

## Notes

- `Lokalita:` is present in only part of the current dataset and describes area
  characteristics rather than municipality identity, so it should not be treated as
  a drop-in replacement for city or district fields.
- If a normalized field cannot be populated without heuristics, make that limitation
  explicit in the contract or metadata instead of silently over-parsing the title.
