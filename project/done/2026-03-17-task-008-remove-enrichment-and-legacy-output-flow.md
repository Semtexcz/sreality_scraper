---
task: TASK-008
status: "done"
priority: P1
type: refactor
---

# Remove enrichment and legacy output behavior from the scraper path

Task: TASK-008
Status: done
Priority: P1
Type: refactor
Author:
Created: 2026-03-17
Related: TASK-004, TASK-005, TASK-006, TASK-007, TASK-009

## Problem

The current scraper runtime still performs geocoding, generates derived fields, and
posts data to an external API endpoint. Those behaviors conflict with the project goal
of capturing and storing raw source data only.

## Definition of Done

- [x] Remove geocoding from the scraper runtime path.
- [x] Remove API posting from the scraper runtime path.
- [x] Remove or isolate derived-field generation that mutates captured source records.
- [x] Simplify configuration so it only includes values required for fetching and raw persistence.
- [x] Update runtime documentation to reflect the final raw-data-only behavior.

## Notes

- Execute this task after the new service and storage layers exist.
- Prefer deletion of obsolete behavior over retaining dormant branches unless backward compatibility is explicitly required.
- Any deprecated configuration should be clearly documented during the transition.
