---
task: TASK-050
status: "todo"
priority: P1
type: design
---

# Design a source-backed raw-coordinate contract

Task: TASK-050
Status: todo
Priority: P1
Type: design
Author:
Created: 2026-03-19
Related: TASK-012, TASK-048, TASK-049

## Problem

The current implementation can recover precise listing coordinates only when the
raw dataset preserves full detail HTML in `raw_page_snapshot`. Most existing raw
records do not persist that snapshot, so replay alone cannot recover the
source-backed GPS points already exposed by Sreality detail pages. The project
needs an approved raw-contract design for carrying replay-safe source-backed
coordinates directly in `source_payload` without requiring full HTML retention.

## Definition of Done

- [ ] Define the canonical scraper-owned raw fields for source-backed detail
      coordinates extracted from the embedded locality payload.
- [ ] Specify whether the raw contract should store only latitude/longitude or
      also keep source provenance and source precision hints alongside them.
- [ ] Define the precedence between raw embedded coordinates and
      `raw_page_snapshot`-based recovery so downstream normalization remains
      deterministic during migration.
- [ ] Document any backward-compatibility and artifact-versioning impacts on raw
      storage, normalization, and replay workflows.
- [ ] Document the parser boundary explicitly so map-link query parameters and
      weaker presentation hints do not enter the raw contract implicitly.

## Notes

- Favor storing only replay-safe fields that are deterministic direct source
  facts rather than presentation-derived guesses.
- Keep the design compatible with older raw artifacts that may still omit the
  new coordinate fields.
- The goal is to reduce dependence on storing full detail HTML for future raw
  captures, not to break existing snapshot-based replay.
