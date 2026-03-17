---
task: TASK-005
status: "done"
priority: P1
type: refactor
---

# Refactor the scraper into explicit services and classes

Task: TASK-005
Status: done
Priority: P1
Type: refactor
Author:
Created: 2026-03-17
Related: TASK-002, TASK-004, TASK-006, TASK-008, TASK-009

## Problem

The scraper runtime is currently concentrated in one large procedural module with
multiple responsibilities. That makes testing difficult, hides dependencies, and
prevents clean separation between acquisition, parsing, and persistence concerns.

## Definition of Done

- [x] Extract HTTP fetching into dedicated client classes.
- [x] Extract listing-page and detail-page parsing into dedicated parser classes.
- [x] Introduce an orchestration service that coordinates discovery and raw record collection.
- [x] Remove direct persistence and delivery side effects from parsing logic.
- [x] Ensure new modules, classes, and functions include docstrings and type hints.
- [x] Preserve behavior needed for raw data acquisition while preparing the codebase for storage abstraction and CLI integration.

## Notes

- Keep classes small, explicit, and single-purpose.
- Favor composition over inheritance unless inheritance is clearly justified.
- Constructor injection should be the default for runtime collaborators.
