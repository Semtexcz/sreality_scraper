---
task: TASK-025
status: "done"
priority: P1
type: feature
---

# Implement nearby places normalization

Task: TASK-025
Status: done
Priority: P1
Type: feature
Author:
Created: 2026-03-18
Related: TASK-024

## Problem

Once the nearby-places contract is defined, normalization should emit
structured nearby-place entries directly from raw detail payload fields instead
of leaving those facts only in source-specific overflow strings. This keeps the
normalized contract easier to query and avoids repeated downstream parsing.

## Definition of Done

- [x] Extend normalization models and runtime to emit typed nearby-place
      entries for all supported source categories.
- [x] Parse source values such as `ZŠ Kouřim(352 m)` into explicit `name` and
      integer `distance_m` fields while preserving the original `source_text`.
- [x] Keep malformed or unsupported nearby-place values traceable without
      failing normalization for the whole listing.
- [x] Add focused unit tests and at least one regression fixture derived from
      persisted snapshots.
- [x] Update normalization contract documentation and any version constants that
      change because of the new field.

## Notes

- Nearby-place parsing should remain deterministic and source-backed only.
- Do not infer travel mode, quality, or ranking from the source categories.
