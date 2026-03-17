---
task: TASK-004
status: "done"
priority: P1
type: design
---

# Design the target architecture for raw data acquisition

Task: TASK-004
Status: done
Priority: P1
Type: design
Author:
Created: 2026-03-17
Related: TASK-003, TASK-005, TASK-006, TASK-007, TASK-008

## Problem

The current implementation mixes HTTP access, HTML parsing, geocoding, MongoDB access,
and API submission in one procedural runtime path. That structure does not match the
new project goal of downloading and persisting raw data from `sreality.cz` without
further processing.

## Definition of Done

- [x] Define the target application layers for CLI, orchestration, scraping, parsing, and persistence.
- [x] Define the core classes and interfaces with responsibilities aligned to SOLID principles.
- [x] Define the raw record contract and explicitly exclude enrichment, normalization, and derived fields from it.
- [x] Identify which existing modules are transitional and should be removed or replaced during the refactor.
- [x] Update architecture documentation to reflect the approved target structure.

## Notes

- Keep dependencies flowing inward toward stable abstractions.
- Prefer explicit constructor-injected dependencies over hidden global runtime state.
- The output of this task should guide implementation tasks rather than introduce code by itself.
